from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import SportsDBClient, SportsDBError, build_games, format_start
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SHLCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls TheSportsDB for today's SHL games."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: SportsDBClient,
        teams: list[str] | None,
        show_upcoming: bool,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self.teams = teams
        self.show_upcoming = show_upcoming

    async def _async_update_data(self) -> dict[str, Any]:
        now_utc = dt_util.utcnow()
        local_today = dt_util.now().date()
        try:
            events = await self.client.events_on_day(now_utc.date())
            # Late games in the local timezone can fall on another UTC date
            if local_today != now_utc.date():
                events += await self.client.events_on_day(local_today)
            today = [
                g
                for g in build_games(events, self.teams)
                if g["start_time"] is None
                or dt_util.as_local(dt_util.parse_datetime(g["start_time"])).date()
                == local_today
            ]

            next_game = last_game = None
            if self.show_upcoming and not today:
                upcoming = build_games(await self.client.next_events(), self.teams)
                recent = build_games(await self.client.past_events(), self.teams)
                next_game = upcoming[0] if upcoming else None
                last_game = recent[-1] if recent else None
        except SportsDBError as err:
            raise UpdateFailed(str(err)) from err

        games = today
        if not games:
            games = [g for g in (last_game, next_game) if g]

        for game in games:
            self._add_local_start(game, local_today)

        return {
            "games": games,
            "today_count": len(today),
            "next_game": next_game,
            "last_game": last_game,
        }

    @staticmethod
    def _add_local_start(game: dict[str, Any], local_today) -> None:
        """Add start_time_local, and show it as the status of games not yet started."""
        start = dt_util.parse_datetime(game["start_time"] or "")
        if start is None:
            game["start_time_local"] = None
            return
        local_start = dt_util.as_local(start)
        game["start_time_local"] = local_start.strftime("%H:%M")
        if game["game_state"] == 0 and not game["status"]:
            game["status"] = format_start(local_start, local_today)

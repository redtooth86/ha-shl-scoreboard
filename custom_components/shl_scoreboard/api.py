"""TheSportsDB v1 client and parsing for the Swedish Hockey League.

This module has no Home Assistant imports so it can be tested on its own.
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

import aiohttp

from .const import (
    API_BASE,
    FINAL_STATUSES,
    LEAGUE_ID,
    LIVE_STATUSES,
    POSTPONED_STATUSES,
    STATUS_TEXT,
    TEAM_ABBREVIATIONS,
)

_LOGGER = logging.getLogger(__name__)


class SportsDBError(Exception):
    """Raised when TheSportsDB cannot be reached or returns bad data."""


class SportsDBRateLimited(SportsDBError):
    """Raised when TheSportsDB answers 429 (free key: ~30 requests/minute)."""


class SportsDBClient:
    """Minimal async client for the TheSportsDB v1 JSON API."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str) -> None:
        self._session = session
        self._api_key = api_key or "123"

    async def _get(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{API_BASE}/{self._api_key}/{endpoint}"
        try:
            async with self._session.get(
                url, params=params, timeout=aiohttp.ClientTimeout(total=20)
            ) as resp:
                if resp.status == 429:
                    raise SportsDBRateLimited("TheSportsDB rate limit reached")
                if resp.status != 200:
                    raise SportsDBError(f"HTTP {resp.status} from {endpoint}")
                # TheSportsDB sometimes serves JSON as text/html
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise SportsDBError(f"Error talking to TheSportsDB: {err}") from err
        except ValueError as err:
            raise SportsDBError(f"Invalid JSON from {endpoint}") from err
        return data or {}

    async def events_on_day(self, day: date) -> list[dict[str, Any]]:
        """All SHL events on a given (UTC) date."""
        data = await self._get(
            "eventsday.php", {"d": day.isoformat(), "s": "Ice_Hockey"}
        )
        events = data.get("events") or []
        return [e for e in events if str(e.get("idLeague")) == LEAGUE_ID]

    async def next_events(self) -> list[dict[str, Any]]:
        data = await self._get("eventsnextleague.php", {"id": LEAGUE_ID})
        return data.get("events") or []

    async def past_events(self) -> list[dict[str, Any]]:
        data = await self._get("eventspastleague.php", {"id": LEAGUE_ID})
        return data.get("events") or []


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def team_abbr(name: str | None) -> str:
    if not name:
        return ""
    if name in TEAM_ABBREVIATIONS:
        return TEAM_ABBREVIATIONS[name]
    return name.replace(" ", "")[:3].upper()


def game_state(status: str | None, home_score: int | None) -> int:
    """0 = pre-game, 1 = in progress, 2 = completed (MyScoreboard convention)."""
    status = (status or "").strip()
    if status in FINAL_STATUSES:
        return 2
    if status in LIVE_STATUSES:
        return 1
    if status in POSTPONED_STATUSES or status in ("", "NS", "TBD"):
        return 0
    # Unknown status code but a score is present: treat as live
    return 1 if home_score is not None else 0


def parse_event(event: dict[str, Any]) -> dict[str, Any]:
    """Convert a TheSportsDB event to the game dict used by myscoreboard-card."""
    home_score = _int_or_none(event.get("intHomeScore"))
    away_score = _int_or_none(event.get("intAwayScore"))
    status = (event.get("strStatus") or "").strip()
    state = game_state(status, home_score)

    timestamp = event.get("strTimestamp")
    if timestamp:
        start_time = timestamp if timestamp.endswith(("Z", "+00:00")) else f"{timestamp}+00:00"
    elif event.get("dateEvent") and event.get("strTime"):
        start_time = f"{event['dateEvent']}T{event['strTime']}+00:00"
    else:
        start_time = None

    home = event.get("strHomeTeam") or ""
    away = event.get("strAwayTeam") or ""

    return {
        "id": event.get("idEvent"),
        "game_state": state,
        "status": STATUS_TEXT.get(status, status) if state != 0 or status in POSTPONED_STATUSES else "",
        "start_time": start_time,
        "home_team": home,
        "home_abbr": team_abbr(home),
        "home_logo": event.get("strHomeTeamBadge"),
        "home_score": home_score,
        "away_team": away,
        "away_abbr": team_abbr(away),
        "away_logo": event.get("strAwayTeamBadge"),
        "away_score": away_score,
        "venue": event.get("strVenue"),
        "round": _int_or_none(event.get("intRound")),
        "season": event.get("strSeason"),
        "broadcasts": [],
        "playoff_status": None,
    }


def matches_teams(game: dict[str, Any], teams: list[str] | None) -> bool:
    """True when no filter is set or either team matches by name or abbreviation."""
    if not teams:
        return True
    wanted = {t.casefold() for t in teams}
    for side in ("home", "away"):
        if game[f"{side}_abbr"].casefold() in wanted:
            return True
        name = game[f"{side}_team"].casefold()
        if any(w in name for w in wanted):
            return True
    return False


def format_start(local_start: datetime, today: date) -> str:
    """Start time for the card's status column: "19:00", or "Thu 30/10 19:00" on another day."""
    clock = local_start.strftime("%H:%M")
    if local_start.date() == today:
        return clock
    return f"{local_start.strftime('%a')} {local_start.day}/{local_start.month} {clock}"


def build_games(
    events: list[dict[str, Any]], teams: list[str] | None
) -> list[dict[str, Any]]:
    """Parse, filter, de-duplicate and sort events by start time."""
    seen: set[str] = set()
    games = []
    for event in events:
        game = parse_event(event)
        if game["id"] in seen or not matches_teams(game, teams):
            continue
        seen.add(game["id"])
        games.append(game)
    games.sort(key=lambda g: g["start_time"] or "")
    return games

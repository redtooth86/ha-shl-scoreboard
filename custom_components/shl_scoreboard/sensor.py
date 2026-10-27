from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import entry_settings
from .const import CONF_NAME, DOMAIN, LEAGUE_NAME
from .coordinator import SHLCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: SHLCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SHLScoreboardSensor(coordinator, entry)])


class SHLScoreboardSensor(CoordinatorEntity[SHLCoordinator], SensorEntity):
    """Today's SHL games, in the attribute format myscoreboard-card reads.

    State is the number of games in the `games` attribute.
    """

    _attr_icon = "mdi:hockey-sticks"
    _attr_attribution = "Data provided by TheSportsDB"

    def __init__(self, coordinator: SHLCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_scoreboard"
        self._attr_name = entry_settings(entry).get(CONF_NAME) or entry.title
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="SHL Scoreboard",
            manufacturer="TheSportsDB",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.thesportsdb.com/league/4419",
        )

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data["games"])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data
        games = data["games"]
        return {
            "league": LEAGUE_NAME,
            "game_count": len(games),
            "today_count": data["today_count"],
            "live_count": sum(1 for g in games if g["game_state"] == 1),
            "final_count": sum(1 for g in games if g["game_state"] == 2),
            "pre_count": sum(1 for g in games if g["game_state"] == 0),
            "games": games,
            "next_game": data["next_game"],
            "last_game": data["last_game"],
        }

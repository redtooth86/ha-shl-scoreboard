"""SHL Scoreboard: Swedish Hockey League scores from TheSportsDB."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SportsDBClient
from .const import (
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_SHOW_UPCOMING,
    CONF_TEAMS,
    DEFAULT_API_KEY,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import SHLCoordinator

PLATFORMS = [Platform.SENSOR]


def entry_settings(entry: ConfigEntry) -> dict:
    """Options override the values chosen in the initial config flow."""
    return {**entry.data, **entry.options}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    settings = entry_settings(entry)
    client = SportsDBClient(
        async_get_clientsession(hass), settings.get(CONF_API_KEY) or DEFAULT_API_KEY
    )
    coordinator = SHLCoordinator(
        hass,
        client,
        settings.get(CONF_TEAMS) or None,
        settings.get(CONF_SHOW_UPCOMING, True),
        settings.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

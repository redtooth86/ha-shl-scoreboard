from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .api import SportsDBClient, SportsDBError, SportsDBRateLimited
from .const import (
    CONF_API_KEY,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_SHOW_UPCOMING,
    CONF_TEAMS,
    DEFAULT_API_KEY,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)


def _schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME, "SHL")): str,
            vol.Optional(
                CONF_TEAMS, default=", ".join(defaults.get(CONF_TEAMS) or [])
            ): str,
            vol.Optional(
                CONF_SHOW_UPCOMING, default=defaults.get(CONF_SHOW_UPCOMING, True)
            ): bool,
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
            vol.Optional(
                CONF_API_KEY, default=defaults.get(CONF_API_KEY, DEFAULT_API_KEY)
            ): str,
        }
    )


def _clean(user_input: dict[str, Any]) -> dict[str, Any]:
    teams = [t.strip() for t in user_input.get(CONF_TEAMS, "").split(",") if t.strip()]
    return {
        **user_input,
        CONF_NAME: user_input.get(CONF_NAME, "").strip() or "SHL",
        CONF_TEAMS: teams,
        CONF_API_KEY: user_input.get(CONF_API_KEY, "").strip() or DEFAULT_API_KEY,
    }


async def _validate(hass, api_key: str) -> str | None:
    client = SportsDBClient(async_get_clientsession(hass), api_key)
    try:
        await client.events_on_day(dt_util.utcnow().date())
    except SportsDBRateLimited:
        return "rate_limited"
    except SportsDBError:
        return "cannot_connect"
    return None


class SHLScoreboardConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            data = _clean(user_input)
            await self.async_set_unique_id(f"{DOMAIN}_{data[CONF_NAME].casefold()}")
            self._abort_if_unique_id_configured()
            error = await _validate(self.hass, data[CONF_API_KEY])
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(title=data[CONF_NAME], data=data)

        return self.async_show_form(
            step_id="user", data_schema=_schema({}), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return SHLScoreboardOptionsFlow()


class SHLScoreboardOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=_clean(user_input))

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_schema(current))

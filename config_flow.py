"""Config flow for GEF Vision integration."""
from __future__ import annotations

import logging
from typing import Any, Mapping
from httpx import ConnectError, ConnectTimeout
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_UNIQUE_ID,
)
from homeassistant.data_entry_flow import FlowResult
from .api_client.client import Client
from .api_client.api.authentication import (
    api_v2_auth_token_create,
)
from .api_client.models import AuthToken

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, VISION_BASE_URL

_LOGGER = logging.getLogger(__name__)

GEF_VISION_DATA_SCHEMA = {
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Required(CONF_UNIQUE_ID): str,
    vol.Required(
        CONF_SCAN_INTERVAL,
        default=DEFAULT_SCAN_INTERVAL,
    ): int,
}

GEF_VISION_REAUTH_SCHEMA = vol.Schema({vol.Required(CONF_PASSWORD): str})
GEF_VISION_USER_SCHEMA = vol.Schema(GEF_VISION_DATA_SCHEMA)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(GEF_VISION_DATA_SCHEMA)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GEF Vision."""

    VERSION = 1

    def __init__(self) -> None:
        self._reauth = False
        self._username = None
        self._password = None
        self._unique_id = None
        self._scan_interval = 0

    async def _async_show_error_form(
        self, errors: dict, error_step: str, schema: vol.Schema
    ) -> FlowResult:
        return self.async_show_form(
            step_id=error_step, data_schema=schema, errors=errors
        )

    async def _async_validate_config(self) -> FlowResult:
        """Attempts to connect to GEF Vision using the provided credentials"""
        client = Client(VISION_BASE_URL)
        auth = AuthToken(username=self._username, password=self._password, token="")

        if self._scan_interval < 10:
            return await self._async_show_error_form(
                {"base": "invalid_parameter"}, "user", GEF_VISION_USER_SCHEMA
            )

        try:
            token = await api_v2_auth_token_create.asyncio(
                client=client, json_body=auth
            )
            if not token:
                return await self._async_show_error_form(
                    {"base": "invalid_auth"}, "user", GEF_VISION_USER_SCHEMA
                )
        except (ConnectError, ConnectTimeout):
            return await self._async_show_error_form(
                {"base": "cannot_connect"}, "user", GEF_VISION_USER_SCHEMA
            )

        if self._reauth:
            entry = await self.async_set_unique_id(self._unique_id)
            if entry:
                self.hass.config_entries.async_update_entry(
                    entry, data={**entry.data, CONF_PASSWORD: self._password}
                )
                self.hass.async_create_task(
                    self.hass.config_entries.async_reload(entry.entry_id)
                )
                return self.async_abort(reason="reauth_successful")
        return self.async_create_entry(
            title=self._username.lower(),
            data={
                CONF_USERNAME: self._username,
                CONF_PASSWORD: self._password,
                CONF_SCAN_INTERVAL: self._scan_interval,
                CONF_UNIQUE_ID: self._unique_id,
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            self._reauth = False
            self._scan_interval = user_input[CONF_SCAN_INTERVAL]
            self._username = user_input[CONF_USERNAME]
            self._password = user_input[CONF_PASSWORD]
            self._unique_id = user_input[CONF_UNIQUE_ID]
            await self.async_set_unique_id(self._unique_id)
            self._abort_if_unique_id_configured()
            return await self._async_validate_config()

        return self.async_show_form(step_id="user", data_schema=GEF_VISION_USER_SCHEMA)

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        self._reauth = True
        self._username = entry_data[CONF_USERNAME]
        self._scan_interval = entry_data[CONF_SCAN_INTERVAL]
        self._unique_id = entry_data[CONF_UNIQUE_ID]
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm reauth dialog."""
        if not user_input:
            return self.async_show_form(
                step_id="reauth_confirm", data_schema=GEF_VISION_REAUTH_SCHEMA
            )
        self._password = user_input[CONF_PASSWORD]
        return await self._async_validate_config()

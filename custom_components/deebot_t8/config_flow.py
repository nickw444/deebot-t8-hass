"""Config flow for Deebot T8 integration."""
from __future__ import annotations

import logging
import time
from typing import Any

import voluptuous as vol
from deebot_t8 import PortalClient, DeebotAuthClient
from deebot_t8.exceptions import InvalidCredentialsException
from deebot_t8.md5 import md5_hex

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from .const import (
    DOMAIN, SERVER_CONTINENTS, SERVER_COUNTRIES, ATTR_CONTINENT,
    ATTR_COUNTRY, ATTR_PASSWORD, ATTR_EMAIL, ATTR_PASSWORD_HASH,
    ATTR_DEVICE_ID)

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_EMAIL): str,
        vol.Required(ATTR_PASSWORD): str,
        vol.Required(ATTR_COUNTRY): vol.In(SERVER_COUNTRIES),
        vol.Required(ATTR_CONTINENT, description="about_continent"): vol.In(SERVER_CONTINENTS),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[
    str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    device_id = md5_hex(str(time.time()))
    continent = data[ATTR_CONTINENT]
    country = data[ATTR_COUNTRY]
    email = data[ATTR_EMAIL]
    password = data[ATTR_PASSWORD]
    password_hash = md5_hex(password)

    portal_client = PortalClient(device_id=device_id, country=country,
                                 continent=continent)
    auth_client = DeebotAuthClient(portal_client=portal_client,
                                   device_id=device_id, country=country)
    try:
        await hass.async_add_executor_job(
            auth_client.login, email, password_hash
        )
    except InvalidCredentialsException:
        raise InvalidAuth

    return {
        ATTR_DEVICE_ID: device_id,
        ATTR_EMAIL: email,
        ATTR_PASSWORD_HASH: password_hash,
        ATTR_COUNTRY: country,
        ATTR_CONTINENT: continent,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Deebot T8."""

    VERSION = 1

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            data = await validate_input(self.hass, user_input)
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title="Ecovacs DEEBOT OZMO T8",
                                           data=data)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

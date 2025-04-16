"""Config flow for Brisk Water integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_MAC_ADDRESS
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC_ADDRESS): str,
    }
)


class BriskWaterConfigFlow(config_entries.ConfigFlow, domain="brisk_water"):
    """Config flow for Brisk Water."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # Validation (you can add more validation here if needed)
        mac_address = user_input[CONF_MAC_ADDRESS]
        if not mac_address:
            return self.async_abort(reason="invalid_mac_address")

        return self.async_create_entry(title="Brisk Water", data=user_input)
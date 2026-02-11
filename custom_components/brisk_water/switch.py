"""Brisk Water switch platform."""

from __future__ import annotations

import logging
from typing import Any

import requests
import json
import voluptuous as vol

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC_ADDRESS
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

# Define the schema for configuration.yaml (if you choose to support YAML configuration)
PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MAC_ADDRESS): cv.string,
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Brisk Water switch from a config entry."""
    mac_address = config_entry.data.get(CONF_MAC_ADDRESS)

    if not mac_address:
        _LOGGER.error("MAC address is not configured.")
        return

    async_add_entities([BriskWaterValveSwitch(mac_address)], True)


class BriskWaterValveSwitch(SwitchEntity):
    """Representation of a Brisk Water valve switch."""

    _attr_name = "Water Valve"  # Default name

    def __init__(self, mac_address: str) -> None:
        """Initialize the switch."""
        self._mac_address = mac_address
        self._attr_is_on = False  # Initially assume the valve is off
        self._available = False
        self._data = {}  # Store the latest data

    async def async_update(self) -> None:
        """Fetch new state data for the switch."""
        try:
            data = await self.fetch_data()
            if data and data.get("resCode") == "0":
                self._data = data["data"]
                self._attr_available = True
                # Assuming data01 represents the valve state (1 for on, 0 for off)
                valve_state = self._data.get("data01")
                if valve_state is not None:
                    self._attr_is_on = valve_state == 1
                else:
                    _LOGGER.warning("Valve state (data01) not found in API response.")
            else:
                self._attr_available = False
                _LOGGER.warning("Failed to fetch data or API returned an error.")
        except Exception as e:
            self._attr_available = False
            _LOGGER.error(f"Error updating switch: {e}")

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the valve on."""
        if await self.send_command(1):  # Assuming 1 is the command to turn on
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the valve off."""
        if await self.send_command(0):  # Assuming 0 is the command to turn off
            self._attr_is_on = False
            self.async_write_ha_state()

    async def fetch_data(self) -> dict[str, Any] | None:
        """Fetch data from the Brisk Water API."""
        url = "http://interface.briskworld.com/devSta/getState/app"
        headers = {
            "Accept-Language": "en-US;q=1",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "interface.briskworld.com",
            "User-Agent": "BriskWater/1.8.6 (iPhone; iOS 17.5.1; Scale/3.00)",
        }
        data = {
            "device": self._mac_address,
            "deviceModel": "BSK_BR",
        }
        try:
            response = await hass.async_add_executor_job(requests.post, url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"Error fetching data: {e}")
            return None
        except json.JSONDecodeError as e:
            _LOGGER.error(f"Error decoding JSON: {e}")
            return None

    async def send_command(self, state: int) -> bool:
        """Send a command to the device to turn the valve on or off."""
        #  IMPORTANT:  You'll need to determine the correct API endpoint and data format
        #  for controlling the valve.  This is a placeholder!
        command_url = "http://interface.briskworld.com/devSta/setValve/app"  # Placeholder URL
        command_data = {
            "device": self._mac_address,
            "deviceModel": "BSK_BR",
            "valve_state": state,  # 1 for on, 0 for off (adjust if needed)
        }
        try:
            response = await hass.async_add_executor_job(requests.post, command_url, headers=self.fetch_headers(), data=command_data)
            response.raise_for_status()
            response_json = response.json()
            if response_json.get("resCode") == "0":
                return True
            else:
                _LOGGER.error(f"Failed to send command: {response_json.get('resMsg')}")
                return False
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"Error sending command: {e}")
            return False
        except json.JSONDecodeError as e:
            _LOGGER.error(f"Error decoding JSON response: {e}")
            return False

    def fetch_headers(self) -> dict[str, str]:
        """Return the headers used for API requests."""
        return {
            "Accept-Language": "en-US;q=1",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "interface.briskworld.com",
            "User-Agent": "BriskWater/1.8.6 (iPhone; iOS 17.5.1; Scale/3.00)",
        }
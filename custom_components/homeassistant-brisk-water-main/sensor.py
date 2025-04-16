"""Brisk Water sensor platform."""

from __future__ import annotations

import logging
from typing import Any

import requests
import json

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import (
    TEMP_KELVIN,
    VOLUME_GALLON,
    UnitOfFlowRate,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Brisk Water sensor."""
    mac_address = config_entry.data.get("mac_address")  # Get MAC address from config entry

    if not mac_address:
        _LOGGER.error("MAC address is not configured.")
        return

    async_add_entities(
        [
            BriskWaterTemperatureSensor(mac_address),
            BriskWaterWaterUsageSensor(mac_address),
            BriskWaterFlowRateSensor(mac_address),
        ],
        True,
    )


class BriskWaterSensor(SensorEntity):
    """Base class for Brisk Water sensors."""

    _attr_has_entity_name = True

    def __init__(self, mac_address: str) -> None:
        """Initialize the sensor."""
        self._mac_address = mac_address
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = None
        self._data = {}  # Store the latest data from the API

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            data = await self.fetch_data()
            if data and data.get("resCode") == "0":
                self._data = data["data"]
                self._attr_available = True
            else:
                self._attr_available = False
                _LOGGER.warning("Failed to fetch data or API returned an error.")
        except Exception as e:
            self._attr_available = False
            _LOGGER.error(f"Error updating sensor: {e}")

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
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"Error fetching data: {e}")
            return None
        except json.JSONDecodeError as e:
            _LOGGER.error(f"Error decoding JSON: {e}")
            return None


class BriskWaterTemperatureSensor(BriskWaterSensor, SensorEntity):
    """Representation of a Brisk Water temperature sensor."""

    _attr_name = "Temperature"
    _attr_native_unit_of_measurement = TEMP_KELVIN
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    @property
    def native_value(self) -> float | None:
        """Return the temperature in Kelvin."""
        if self._data:
            return self._data.get("data04")
        return None


class BriskWaterWaterUsageSensor(BriskWaterSensor, SensorEntity):
    """Representation of a Brisk Water water usage sensor."""

    _attr_name = "Water Usage"
    _attr_native_unit_of_measurement = VOLUME_GALLON
    _attr_device_class = SensorDeviceClass.WATER

    @property
    def native_value(self) -> float | None:
        """Return the water usage in gallons."""
        if self._data:
            return self._data.get("data10")
        return None


class BriskWaterFlowRateSensor(BriskWaterSensor, SensorEntity):
    """Representation of a Brisk Water flow rate sensor."""

    _attr_name = "Flow Rate"
    _attr_native_unit_of_measurement = UnitOfFlowRate.LITERS_PER_HOUR

    @property
    def native_value(self) -> float | None:
        """Return the flow rate in liters per hour."""
        if self._data:
            return self._data.get("data0B")
        return None
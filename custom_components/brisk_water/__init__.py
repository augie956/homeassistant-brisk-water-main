"""Brisk Water integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

# List of platforms to support.
# Each platform file must be located in the same directory.
PLATFORMS: list[Platform] = [Platform.SENSOR]  # Add Platform.SWITCH if you implement valve control


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Brisk Water from a config entry."""
    # This is a placeholder; we'll add actual setup logic later if needed.
    # For now, we just forward the setup to the platforms.

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Placeholder for cleanup if needed
        pass
    return unload_ok
"""Diagnostics support for MicroAirEasyTouch integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Keys to redact from diagnostics
TO_REDACT = {
    "SN",  # Serial number
    "EM",  # Email
    "password",
    "username",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]["data"]

    diagnostics_data = {
        "entry": {
            "title": entry.title,
            "unique_id": entry.unique_id,
        },
        "device_state": {},
        "raw_data": {},
    }

    # Try to get the current state from climate entity
    for entity_id, state in hass.states.async_all():
        if (
            entity_id.startswith("climate.")
            and entry.entry_id in entity_id
            or f"microaireasytouch_{entry.unique_id}" in entity_id
        ):
            diagnostics_data["device_state"][entity_id] = {
                "state": state.state,
                "attributes": dict(state.attributes),
            }

    # Get raw device data if available
    if hasattr(data, "_client") and data._client:
        diagnostics_data["bluetooth_connected"] = (
            data._client.is_connected if data._client else False
        )

    # Log information about what data points are being tracked
    _LOGGER.info("=== MicroAir EasyTouch Diagnostics ===")
    _LOGGER.info("Available data in parser:")
    _LOGGER.info(
        "  - Temperature setpoints: autoHeat_sp, autoCool_sp, cool_sp, heat_sp, dry_sp"
    )
    _LOGGER.info(
        "  - Fan modes: fan_mode_num, cool_fan_mode_num, heat_fan_mode_num,"
    )
    _LOGGER.info("               auto_fan_mode_num, dry_fan_mode_num")
    _LOGGER.info("  - Modes: mode_num (setpoint), current_mode_num (actual)")
    _LOGGER.info("  - Temperature: facePlateTemperature")
    _LOGGER.info("  - Power state: param[7]=off, param[15]=on")
    _LOGGER.info("  - Raw info array indices:")
    _LOGGER.info(
        "      [0]=autoHeat_sp, [1]=autoCool_sp, [2]=cool_sp, [3]=heat_sp"
    )
    _LOGGER.info("      [4]=dry_sp, [5]=dry_fan, [6]=fan_mode, [7]=cool_fan")
    _LOGGER.info(
        "      [8]=unknown, [9]=auto_fan, [10]=mode_num, [11]=heat_fan"
    )
    _LOGGER.info(
        "      [12]=temperature, [13-14]=unknown, [15]=current_mode_num"
    )
    _LOGGER.info("      [16+]=unknown (if present)")
    _LOGGER.info("=====================================")

    return async_redact_data(diagnostics_data, TO_REDACT)


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    return await async_get_config_entry_diagnostics(hass, entry)

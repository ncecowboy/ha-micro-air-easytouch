"""Service handlers for MicroAirEasyTouch integration."""

from __future__ import annotations

import logging
import time

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN
from .micro_air_easytouch.parser import MicroAirEasyTouchBluetoothDeviceData

_LOGGER = logging.getLogger(__name__)

# Service schema for validation
SERVICE_SET_LOCATION_SCHEMA = vol.Schema(
    {
        vol.Required("address"): cv.string,
        vol.Required("latitude"): vol.All(
            vol.Coerce(float), vol.Range(min=-90.0, max=90.0)
        ),
        vol.Required("longitude"): vol.All(
            vol.Coerce(float), vol.Range(min=-180.0, max=180.0)
        ),
    }
)

SERVICE_QUERY_DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required("address"): cv.string,
    }
)


async def async_register_services(hass: HomeAssistant) -> None:
    """Register services for the MicroAirEasyTouch integration."""

    async def handle_set_location(call: ServiceCall) -> None:
        """Handle the set_location service call."""
        address = call.data.get("address")
        latitude = call.data.get("latitude")
        longitude = call.data.get("longitude")

        # Find the config entry by MAC address (unique_id)
        config_entry = None
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.unique_id == address:
                config_entry = entry
                break

        if not config_entry:
            _LOGGER.error(
                "No MicroAirEasyTouch config entry found for address %s",
                address,
            )
            return

        # Get the device data
        device_data: MicroAirEasyTouchBluetoothDeviceData = hass.data[DOMAIN][
            config_entry.entry_id
        ]["data"]
        mac_address = config_entry.unique_id
        assert mac_address is not None

        # Get BLE device
        ble_device = async_ble_device_from_address(hass, mac_address)
        if not ble_device:
            _LOGGER.error(
                "Could not find BLE device for address %s", mac_address
            )
            return

        # Construct the command
        command = {
            "Type": "Get Status",
            "Zone": 0,
            "LAT": f"{latitude:.5f}",
            "LON": f"{longitude:.5f}",
            "TM": int(time.time()),
        }

        # Send the command
        try:
            success = await device_data.send_command(hass, ble_device, command)
            if success:
                _LOGGER.info(
                    "Successfully sent location (LAT: %s, LON: %s) to device %s",
                    latitude,
                    longitude,
                    mac_address,
                )
            else:
                _LOGGER.error(
                    "Failed to send location command to device %s", mac_address
                )
        except Exception as e:
            _LOGGER.error(
                "Error sending location command to device %s: %s",
                mac_address,
                str(e),
            )

    async def handle_query_device(call: ServiceCall) -> None:
        """Handle the query_device service call to discover all available data."""
        address = call.data.get("address")

        # Find the config entry by MAC address (unique_id)
        config_entry = None
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.unique_id == address:
                config_entry = entry
                break

        if not config_entry:
            _LOGGER.error(
                "No MicroAirEasyTouch config entry found for address %s",
                address,
            )
            return

        # Get the device data
        device_data: MicroAirEasyTouchBluetoothDeviceData = hass.data[DOMAIN][
            config_entry.entry_id
        ]["data"]
        mac_address = config_entry.unique_id
        assert mac_address is not None

        # Get BLE device
        ble_device = async_ble_device_from_address(hass, mac_address)
        if not ble_device:
            _LOGGER.error(
                "Could not find BLE device for address %s", mac_address
            )
            return

        # Query device status
        command = {
            "Type": "Get Status",
            "Zone": 0,
            "EM": device_data._email,
            "TM": int(time.time()),
        }

        try:
            _LOGGER.info(
                "=== Querying device %s for all available data ===", address
            )
            if await device_data.send_command(hass, ble_device, command):
                from .micro_air_easytouch.const import UUIDS

                json_payload = await device_data._read_gatt_with_retry(
                    hass, UUIDS["jsonReturn"], ble_device
                )
                if json_payload:
                    import json

                    raw_data = json.loads(json_payload.decode("utf-8"))
                    parsed_data = device_data.decrypt(
                        json_payload.decode("utf-8")
                    )

                    _LOGGER.info("RAW DEVICE RESPONSE:")
                    _LOGGER.info(
                        "  Full JSON: %s", json.dumps(raw_data, indent=2)
                    )
                    _LOGGER.info("")
                    _LOGGER.info("PARSED DATA:")
                    for key, value in parsed_data.items():
                        if key != "ALL":
                            _LOGGER.info("  %s: %s", key, value)
                    _LOGGER.info("")
                    _LOGGER.info("RAW INFO ARRAY (Z_sts['0']):")
                    if "Z_sts" in raw_data and "0" in raw_data["Z_sts"]:
                        info_array = raw_data["Z_sts"]["0"]
                        for idx, val in enumerate(info_array):
                            _LOGGER.info("  info[%d] = %s", idx, val)
                    _LOGGER.info("")
                    _LOGGER.info("PARAMETERS (PRM):")
                    if "PRM" in raw_data:
                        _LOGGER.info("  %s", raw_data["PRM"])
                    _LOGGER.info("")
                    _LOGGER.info("BLUETOOTH UUIDs available:")
                    _LOGGER.info("  service: %s", UUIDS["service"])
                    _LOGGER.info("  passwordCmd: %s", UUIDS["passwordCmd"])
                    _LOGGER.info("  jsonCmd: %s", UUIDS["jsonCmd"])
                    _LOGGER.info("  jsonReturn: %s", UUIDS["jsonReturn"])
                    _LOGGER.info("  unknown: %s", UUIDS["unknown"])
                    _LOGGER.info(
                        "=============================================="
                    )
                else:
                    _LOGGER.error("No response received from device")
            else:
                _LOGGER.error("Failed to send query command to device")
        except Exception as e:
            _LOGGER.error("Error querying device %s: %s", mac_address, str(e))

    # Register the services
    hass.services.async_register(
        DOMAIN,
        "set_location",
        handle_set_location,
        schema=SERVICE_SET_LOCATION_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "query_device",
        handle_query_device,
        schema=SERVICE_QUERY_DEVICE_SCHEMA,
    )


async def async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister services for the MicroAirEasyTouch integration."""
    hass.services.async_remove(DOMAIN, "set_location")
    hass.services.async_remove(DOMAIN, "query_device")

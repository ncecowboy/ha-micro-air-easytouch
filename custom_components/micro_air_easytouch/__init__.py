"""MicroAirEasyTouch Integration"""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Final

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_ble_device_from_address,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .micro_air_easytouch.const import UUIDS
from .micro_air_easytouch.parser import MicroAirEasyTouchBluetoothDeviceData
from .services import async_register_services, async_unregister_services

PLATFORMS: Final = [Platform.BUTTON, Platform.CLIMATE, Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)

# Update interval for coordinator - poll every 2 minutes
UPDATE_INTERVAL = timedelta(seconds=120)


class MicroAirEasyTouchCoordinator(DataUpdateCoordinator):
    """Coordinator to manage single Bluetooth connection for all entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        data: MicroAirEasyTouchBluetoothDeviceData,
        address: str,
        zone: int = 0,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{address}",
            update_interval=UPDATE_INTERVAL,
        )
        self._data = data
        self._address = address
        self._zone = zone

    async def _async_update_data(self) -> dict:
        """Fetch data from the device using a single Bluetooth connection."""
        ble_device = async_ble_device_from_address(self.hass, self._address)
        if not ble_device:
            raise UpdateFailed(f"Could not find BLE device: {self._address}")

        message = {
            "Type": "Get Status",
            "Zone": self._zone,
            "EM": self._data._email,
            "TM": int(time.time()),
        }

        try:
            if await self._data.send_command(self.hass, ble_device, message):
                json_payload = await self._data._read_gatt_with_retry(
                    self.hass, UUIDS["jsonReturn"], ble_device
                )
                if json_payload:
                    new_state = self._data.decrypt(
                        json_payload.decode("utf-8"), zone=self._zone
                    )
                    if new_state:
                        _LOGGER.debug(
                            "Coordinator fetched state for zone %s",
                            self._zone,
                        )
                        return new_state
                    raise UpdateFailed("Failed to decrypt device data")
                raise UpdateFailed("No payload received from device")
            raise UpdateFailed("Failed to send command to device")
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with device: {err}"
            ) from err


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MicroAirEasyTouch from a config entry."""
    address = entry.unique_id
    assert address is not None
    password = entry.data.get(CONF_PASSWORD)
    email = entry.data.get(CONF_USERNAME)
    data = MicroAirEasyTouchBluetoothDeviceData(password=password, email=email)

    # Create coordinator for centralized data updates
    coordinator = MicroAirEasyTouchCoordinator(hass, data, address, zone=0)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "data": data,
        "coordinator": coordinator,
    }

    @callback
    def _handle_bluetooth_update(
        service_info: BluetoothServiceInfoBleak,
    ) -> None:
        """Update device info from advertisements."""
        if service_info.address == address:
            _LOGGER.debug(
                "Received BLE advertisement from %s: %s", address, service_info
            )
            data._start_update(service_info)

    hass.bus.async_listen("bluetooth_service_info", _handle_bluetooth_update)

    # Register services
    await async_register_services(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    ):
        hass.data[DOMAIN].pop(entry.entry_id)
        # Unregister services
        await async_unregister_services(hass)
    return unload_ok

"""Support for MicroAirEasyTouch sensors."""

from __future__ import annotations

import logging
import time

from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity,
                                             SensorStateClass)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .micro_air_easytouch.const import UUIDS
from .micro_air_easytouch.parser import MicroAirEasyTouchBluetoothDeviceData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MicroAirEasyTouch sensor platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]["data"]
    mac_address = config_entry.unique_id

    entities = [
        MicroAirEasyTouchTemperatureSensor(data, mac_address),
        MicroAirEasyTouchCurrentModeSensor(data, mac_address),
        MicroAirEasyTouchCurrentFanModeSensor(data, mac_address),
        MicroAirEasyTouchSerialNumberSensor(data, mac_address),
    ]

    async_add_entities(entities)


class MicroAirEasyTouchSensorBase(SensorEntity):
    """Base class for MicroAirEasyTouch sensors."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self, data: MicroAirEasyTouchBluetoothDeviceData, mac_address: str
    ) -> None:
        """Initialize the sensor."""
        self._data = data
        self._mac_address = mac_address
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"MicroAirEasyTouch_{mac_address}")},
            name=f"EasyTouch {mac_address}",
            manufacturer="Micro-Air",
            model="Thermostat",
        )
        self._state = {}

    async def async_added_to_hass(self) -> None:
        """Handle entity added to hass."""
        await super().async_added_to_hass()
        # Schedule initial state fetch in background to avoid blocking startup
        self.hass.async_create_task(self._async_fetch_initial_state())

    async def _async_fetch_initial_state(self) -> None:
        """Fetch the initial state from the device."""
        ble_device = async_ble_device_from_address(
            self.hass, self._mac_address
        )
        if not ble_device:
            _LOGGER.error("Could not find BLE device: %s", self._mac_address)
            self._state = {}
            return

        message = {
            "Type": "Get Status",
            "Zone": 0,
            "EM": self._data._email,
            "TM": int(time.time()),
        }
        try:
            if await self._data.send_command(self.hass, ble_device, message):
                json_payload = await self._data._read_gatt_with_retry(
                    self.hass, UUIDS["jsonReturn"], ble_device
                )
                if json_payload:
                    decoded = json_payload.decode("utf-8")
                    self._state = self._data.decrypt(decoded)
                    _LOGGER.debug(
                        "Initial state fetched for sensor: %s", self._state
                    )
                    self.async_write_ha_state()
                else:
                    self._state = {}
                    _LOGGER.warning("No payload received for initial state")
            else:
                self._state = {}
                _LOGGER.warning("Failed to send command for initial state")
        except Exception as e:
            _LOGGER.error("Failed to fetch initial state: %s", str(e))
            self._state = {}

    async def async_update(self) -> None:
        """Update the entity state manually if needed."""
        await self._async_fetch_initial_state()


class MicroAirEasyTouchTemperatureSensor(MicroAirEasyTouchSensorBase):
    """Temperature sensor for MicroAirEasyTouch."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
    _attr_name = "Temperature"

    def __init__(
        self, data: MicroAirEasyTouchBluetoothDeviceData, mac_address: str
    ) -> None:
        """Initialize the temperature sensor."""
        super().__init__(data, mac_address)
        self._attr_unique_id = f"microaireasytouch_{mac_address}_temperature"

    @property
    def native_value(self) -> float | None:
        """Return the current temperature."""
        return self._state.get("facePlateTemperature")

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:thermometer"


class MicroAirEasyTouchCurrentModeSensor(MicroAirEasyTouchSensorBase):
    """Current mode sensor for MicroAirEasyTouch."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Current Mode"

    def __init__(
        self, data: MicroAirEasyTouchBluetoothDeviceData, mac_address: str
    ) -> None:
        """Initialize the current mode sensor."""
        super().__init__(data, mac_address)
        self._attr_unique_id = f"microaireasytouch_{mac_address}_current_mode"

    @property
    def native_value(self) -> str | None:
        """Return the current mode."""
        return self._state.get("current_mode")

    @property
    def icon(self) -> str:
        """Return the icon based on current mode."""
        mode = self._state.get("current_mode")
        mode_icons = {
            "off": "mdi:power-off",
            "fan": "mdi:fan",
            "cool": "mdi:snowflake",
            "cool_on": "mdi:snowflake",
            "heat": "mdi:fire",
            "heat_on": "mdi:fire",
            "dry": "mdi:water-percent",
            "auto": "mdi:autorenew",
        }
        return mode_icons.get(mode, "mdi:thermostat")


class MicroAirEasyTouchCurrentFanModeSensor(MicroAirEasyTouchSensorBase):
    """Current fan mode sensor for MicroAirEasyTouch."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Current Fan Mode"

    def __init__(
        self, data: MicroAirEasyTouchBluetoothDeviceData, mac_address: str
    ) -> None:
        """Initialize the current fan mode sensor."""
        super().__init__(data, mac_address)
        self._attr_unique_id = (
            f"microaireasytouch_{mac_address}_current_fan_mode"
        )

    @property
    def native_value(self) -> str | None:
        """Return the current fan mode based on current mode."""
        current_mode = self._state.get("mode", "off")

        # Map fan modes from parser
        fan_modes_full = {
            0: "off",
            1: "manual low",
            2: "manual high",
            65: "cycled low",
            66: "cycled high",
            128: "full auto",
        }
        fan_modes_fan_only = {0: "off", 1: "low", 2: "high"}

        if current_mode == "fan":
            fan_mode_num = self._state.get("fan_mode_num", 0)
            return fan_modes_fan_only.get(fan_mode_num, "unknown")
        elif current_mode == "cool":
            fan_mode_num = self._state.get("cool_fan_mode_num", 128)
            return fan_modes_full.get(fan_mode_num, "unknown")
        elif current_mode == "heat":
            fan_mode_num = self._state.get("heat_fan_mode_num", 128)
            return fan_modes_full.get(fan_mode_num, "unknown")
        elif current_mode == "auto":
            fan_mode_num = self._state.get("auto_fan_mode_num", 128)
            return fan_modes_full.get(fan_mode_num, "unknown")
        elif current_mode == "dry":
            fan_mode_num = self._state.get("dry_fan_mode_num", 128)
            return fan_modes_full.get(fan_mode_num, "unknown")
        return "off"

    @property
    def icon(self) -> str:
        """Return the icon based on fan mode."""
        return "mdi:fan"


class MicroAirEasyTouchSerialNumberSensor(MicroAirEasyTouchSensorBase):
    """Serial number sensor for MicroAirEasyTouch."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Serial Number"

    def __init__(
        self, data: MicroAirEasyTouchBluetoothDeviceData, mac_address: str
    ) -> None:
        """Initialize the serial number sensor."""
        super().__init__(data, mac_address)
        self._attr_unique_id = f"microaireasytouch_{mac_address}_serial_number"

    @property
    def native_value(self) -> str | None:
        """Return the serial number."""
        sn = self._state.get("SN")
        return str(sn) if sn is not None else None

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:identifier"

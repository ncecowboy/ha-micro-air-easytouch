"""Support for MicroAirEasyTouch sensors."""

from __future__ import annotations

import json
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .micro_air_easytouch.parser import MicroAirEasyTouchBluetoothDeviceData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MicroAirEasyTouch sensor platform."""
    data = hass.data[DOMAIN][config_entry.entry_id]["data"]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    mac_address = config_entry.unique_id

    # Create sensors for zone 0 only
    entities = [
        MicroAirEasyTouchTemperatureSensor(
            coordinator, data, mac_address, zone=0
        ),
        MicroAirEasyTouchCurrentModeSensor(
            coordinator, data, mac_address, zone=0
        ),
        MicroAirEasyTouchCurrentFanModeSensor(
            coordinator, data, mac_address, zone=0
        ),
        MicroAirEasyTouchSerialNumberSensor(
            coordinator, data, mac_address, zone=0
        ),
        MicroAirEasyTouchRawInfoArraySensor(
            coordinator, data, mac_address, zone=0
        ),
        MicroAirEasyTouchParametersSensor(
            coordinator, data, mac_address, zone=0
        ),
    ]

    async_add_entities(entities)


class MicroAirEasyTouchSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for MicroAirEasyTouch sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        data: MicroAirEasyTouchBluetoothDeviceData,
        mac_address: str,
        zone: int = 0,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = data
        self._mac_address = mac_address
        self._zone = zone
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"MicroAirEasyTouch_{mac_address}")},
            name=f"EasyTouch {mac_address}",
            manufacturer="Micro-Air",
            model="Thermostat",
        )


class MicroAirEasyTouchTemperatureSensor(MicroAirEasyTouchSensorBase):
    """Temperature sensor for MicroAirEasyTouch."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    def __init__(
        self,
        coordinator,
        data: MicroAirEasyTouchBluetoothDeviceData,
        mac_address: str,
        zone: int = 0,
    ) -> None:
        """Initialize the temperature sensor."""
        super().__init__(coordinator, data, mac_address, zone)
        self._attr_unique_id = f"microaireasytouch_{mac_address}_temperature"
        self._attr_name = "Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.get("facePlateTemperature")

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:thermometer"


class MicroAirEasyTouchCurrentModeSensor(MicroAirEasyTouchSensorBase):
    """Current mode sensor for MicroAirEasyTouch."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator,
        data: MicroAirEasyTouchBluetoothDeviceData,
        mac_address: str,
        zone: int = 0,
    ) -> None:
        """Initialize the current mode sensor."""
        super().__init__(coordinator, data, mac_address, zone)
        self._attr_unique_id = f"microaireasytouch_{mac_address}_current_mode"
        self._attr_name = "Current Mode"

    @property
    def native_value(self) -> str | None:
        """Return the current mode."""
        return self.coordinator.data.get("current_mode")

    @property
    def icon(self) -> str:
        """Return the icon based on current mode."""
        mode = self.coordinator.data.get("current_mode")
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

    def __init__(
        self,
        coordinator,
        data: MicroAirEasyTouchBluetoothDeviceData,
        mac_address: str,
        zone: int = 0,
    ) -> None:
        """Initialize the current fan mode sensor."""
        super().__init__(coordinator, data, mac_address, zone)
        self._attr_unique_id = (
            f"microaireasytouch_{mac_address}_current_fan_mode"
        )
        self._attr_name = "Current Fan Mode"

    @property
    def native_value(self) -> str | None:
        """Return the current fan mode based on current mode."""
        current_mode = self.coordinator.data.get("mode", "off")

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
            fan_mode_num = self.coordinator.data.get("fan_mode_num", 0)
            return fan_modes_fan_only.get(fan_mode_num, "unknown")
        elif current_mode == "cool":
            fan_mode_num = self.coordinator.data.get("cool_fan_mode_num", 128)
            return fan_modes_full.get(fan_mode_num, "unknown")
        elif current_mode == "heat":
            fan_mode_num = self.coordinator.data.get("heat_fan_mode_num", 128)
            return fan_modes_full.get(fan_mode_num, "unknown")
        elif current_mode == "auto":
            fan_mode_num = self.coordinator.data.get("auto_fan_mode_num", 128)
            return fan_modes_full.get(fan_mode_num, "unknown")
        elif current_mode == "dry":
            fan_mode_num = self.coordinator.data.get("dry_fan_mode_num", 128)
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
        self,
        coordinator,
        data: MicroAirEasyTouchBluetoothDeviceData,
        mac_address: str,
        zone: int = 0,
    ) -> None:
        """Initialize the serial number sensor."""
        super().__init__(coordinator, data, mac_address, zone)
        self._attr_unique_id = f"microaireasytouch_{mac_address}_serial_number"

    @property
    def native_value(self) -> str | None:
        """Return the serial number."""
        sn = self.coordinator.data.get("SN")
        return str(sn) if sn is not None else None

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:identifier"


class MicroAirEasyTouchRawInfoArraySensor(MicroAirEasyTouchSensorBase):
    """Raw info array sensor for MicroAirEasyTouch."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Raw Info Array"

    def __init__(
        self,
        coordinator,
        data: MicroAirEasyTouchBluetoothDeviceData,
        mac_address: str,
        zone: int = 0,
    ) -> None:
        """Initialize the raw info array sensor."""
        super().__init__(coordinator, data, mac_address, zone)
        self._attr_unique_id = (
            f"microaireasytouch_{mac_address}_raw_info_array"
        )

    @property
    def native_value(self) -> str | None:
        """Return the raw info array as JSON."""
        all_data = self.coordinator.data.get("ALL")
        zone_key = str(self._zone)
        if all_data and "Z_sts" in all_data and zone_key in all_data["Z_sts"]:
            return json.dumps(all_data["Z_sts"][zone_key])
        return None

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:code-array"

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes with parsed info array indices."""
        all_data = self.coordinator.data.get("ALL")
        zone_key = str(self._zone)
        if all_data and "Z_sts" in all_data and zone_key in all_data["Z_sts"]:
            info = all_data["Z_sts"][zone_key]
            return {
                "info_0_autoHeat_sp": info[0] if len(info) > 0 else None,
                "info_1_autoCool_sp": info[1] if len(info) > 1 else None,
                "info_2_cool_sp": info[2] if len(info) > 2 else None,
                "info_3_heat_sp": info[3] if len(info) > 3 else None,
                "info_4_dry_sp": info[4] if len(info) > 4 else None,
                "info_5_dry_fan": info[5] if len(info) > 5 else None,
                "info_6_fan_mode": info[6] if len(info) > 6 else None,
                "info_7_cool_fan": info[7] if len(info) > 7 else None,
                "info_8_unknown": info[8] if len(info) > 8 else None,
                "info_9_auto_fan": info[9] if len(info) > 9 else None,
                "info_10_mode_num": info[10] if len(info) > 10 else None,
                "info_11_heat_fan": info[11] if len(info) > 11 else None,
                "info_12_temperature": info[12] if len(info) > 12 else None,
                "info_13_unknown": info[13] if len(info) > 13 else None,
                "info_14_unknown": info[14] if len(info) > 14 else None,
                "info_15_current_mode": (info[15] if len(info) > 15 else None),
            }
        return {}


class MicroAirEasyTouchParametersSensor(MicroAirEasyTouchSensorBase):
    """Parameters sensor for MicroAirEasyTouch."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_name = "Parameters"

    def __init__(
        self,
        coordinator,
        data: MicroAirEasyTouchBluetoothDeviceData,
        mac_address: str,
        zone: int = 0,
    ) -> None:
        """Initialize the parameters sensor."""
        super().__init__(coordinator, data, mac_address, zone)
        self._attr_unique_id = f"microaireasytouch_{mac_address}_parameters"

    @property
    def native_value(self) -> str | None:
        """Return the parameters as JSON."""
        all_data = self.coordinator.data.get("ALL")
        if all_data and "PRM" in all_data:
            return json.dumps(all_data["PRM"])
        return None

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:tune"

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra attributes with parameter values."""
        all_data = self.coordinator.data.get("ALL")
        if all_data and "PRM" in all_data:
            prm = all_data["PRM"]
            attrs = {}
            for idx, val in enumerate(prm):
                attrs[f"param_{idx}"] = val
            # Add interpreted values based on documentation
            if 7 in prm:
                attrs["power_off_indicated"] = True
            if 15 in prm:
                attrs["power_on_indicated"] = True
            return attrs
        return {}

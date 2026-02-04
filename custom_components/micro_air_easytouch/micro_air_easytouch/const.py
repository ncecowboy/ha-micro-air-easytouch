"""Constants for MicroAirEasyTouch parser"""

from homeassistant.components.climate import HVACMode

DOMAIN = "micro_air_easytouch"

UUIDS = {
    "service": "000000FF-0000-1000-8000-00805F9B34FB",  # ro
    "passwordCmd": "0000DD01-0000-1000-8000-00805F9B34FB",  # rw
    "jsonCmd": "0000EE01-0000-1000-8000-00805F9B34FB",  # rw
    "jsonReturn": "0000FF01-0000-1000-8000-00805F9B34FB",
    "unknown": "00002a05-0000-1000-8000-00805f9b34fb",
}

# Map EasyTouch modes to Home Assistant HVAC modes
HA_MODE_TO_EASY_MODE = {
    HVACMode.OFF: 0,
    HVACMode.FAN_ONLY: 1,
    HVACMode.COOL: 2,
    HVACMode.HEAT: 4,
    HVACMode.DRY: 6,
    HVACMode.AUTO: 11,
}
# Map device modes to Home Assistant HVAC modes
# Includes both setpoint modes and running modes (cool_on=3, heat_on=5)
EASY_MODE_TO_HA_MODE = {
    0: HVACMode.OFF,
    1: HVACMode.FAN_ONLY,
    2: HVACMode.COOL,
    3: HVACMode.COOL,  # cool_on maps to COOL
    4: HVACMode.HEAT,
    5: HVACMode.HEAT,  # heat_on maps to HEAT
    6: HVACMode.DRY,
    11: HVACMode.AUTO,
}

# Fan mode mappings (general and mode-specific)
FAN_MODES_FULL = {
    "off": 0,
    "manualL": 1,
    "manualH": 2,
    "cycledL": 65,
    "cycledH": 66,
    "full auto": 128,
}
FAN_MODES_FAN_ONLY = {
    "off": 0,
    "low": 1,  # manualL
    "high": 2,  # manualH
}
FAN_MODES_REVERSE = {v: k for k, v in FAN_MODES_FULL.items()}

# Missing Data and Features Analysis

## Overview
This document identifies potential data fields, settings, and features that may not be fully exposed or utilized in the current Micro-Air EasyTouch integration.

## Data Currently NOT Exposed or Used

### 1. Info Array Indices (Z_sts["0"])
The integration accesses 16 values from the info array but **3 are unknown/unused**:

| Index | Currently Used | Status | Notes |
|-------|---------------|--------|-------|
| 0 | ✅ autoHeat_sp | Used | Auto mode heat setpoint |
| 1 | ✅ autoCool_sp | Used | Auto mode cool setpoint |
| 2 | ✅ cool_sp | Used | Cool mode setpoint |
| 3 | ✅ heat_sp | Used | Heat mode setpoint |
| 4 | ✅ dry_sp | Used | Dry mode setpoint |
| 5 | ✅ dry_fan_mode_num | Used | Dry mode fan setting |
| 6 | ✅ fan_mode_num | Used | Fan-only mode setting |
| 7 | ✅ cool_fan_mode_num | Used | Cool mode fan setting |
| 8 | ❌ **UNKNOWN** | **Not used** | **Could be humidity, outdoor temp, or other sensor** |
| 9 | ✅ auto_fan_mode_num | Used | Auto mode fan setting |
| 10 | ✅ mode_num | Used | Mode number |
| 11 | ✅ heat_fan_mode_num | Used | Heat mode fan setting |
| 12 | ✅ facePlateTemperature | Used | Current temperature |
| 13 | ❌ **UNKNOWN** | **Not used** | **Could be outdoor temp, humidity, or other sensor** |
| 14 | ❌ **UNKNOWN** | **Not used** | **Could be return air temp, target reached status, or timer** |
| 15 | ✅ current_mode_num | Used | Current operating mode |

**Action Item**: Indices 8, 13, and 14 are marked as "unknown" in the sensor attributes but their actual values are not analyzed or exposed meaningfully.

### 2. Additional Top-Level JSON Keys
The integration only parses three top-level keys from the device response:
- `Z_sts` - Zone status (currently only zone 0 accessed)
- `PRM` - Parameters array
- `SN` - Serial number

**Potentially Missing Keys** (would need device query to confirm):
- `CFG` or `CONFIG` - Device configuration settings
- `VER` or `VERSION` - Firmware version
- `MODEL` - Model identifier
- `CAPS` or `CAPABILITIES` - Device capabilities flags
- `ERR` or `ERRORS` - Error codes or status
- `TIMER` - Timer settings
- `SCHEDULE` - Schedule/programming data
- `WIFI` - WiFi configuration (if applicable)
- `BT` or `BLUETOOTH` - Bluetooth settings
- `SENSOR` - Additional sensor data
- `FLT` or `FILTER` - Filter status/runtime
- `OUTDOOR` - Outdoor temperature sensor data
- `HUMIDITY` - Humidity sensor data

### 3. PRM (Parameters) Array
Currently, the PRM array is logged and two values are interpreted:
- Parameter index 7: Power off indication
- Parameter index 15: Power on indication

**Unknown parameters** - The full PRM array may contain:
- Setpoint limits (min/max temperatures)
- Fan speed configurations
- Compressor delay settings
- Temperature offsets/calibration
- Display preferences (°F/°C)
- Energy-saving settings
- Filter runtime or maintenance reminders
- Advanced configuration flags

**Action Item**: Other parameter indices are not documented or exposed.

### 4. Command Capabilities
The integration sends these command types:
- `"Type": "Get Status"` - Query device status
- `"Type": "Change"` - Modify settings/reboot

**Potentially Missing Command Types**:
- `"Type": "Get Config"` - Retrieve configuration
- `"Type": "Set Config"` - Modify configuration
- `"Type": "Get Schedule"` - Retrieve programmed schedules
- `"Type": "Set Schedule"` - Program schedules
- `"Type": "Get Filter"` - Filter status
- `"Type": "Reset Filter"` - Reset filter timer
- `"Type": "Get Diagnostics"` - Diagnostic data
- `"Type": "Calibrate"` - Temperature calibration
- `"Type": "Factory Reset"` - Factory reset

### 5. Change Command Parameters
Currently supported change parameters:
- `power` - Power on/off
- `mode` - HVAC mode
- `cool_sp`, `heat_sp`, `dry_sp` - Temperature setpoints
- `autoCool_sp`, `autoHeat_sp` - Auto mode setpoints
- `coolFan`, `heatFan`, `autoFan`, `dryFan`, `fanOnly` - Fan settings
- `reset` - Device reboot
- `zone` - Zone selection

**Potentially Missing Change Parameters**:
- `tempOffset` or `calibration` - Temperature calibration
- `displayUnits` - °F/°C display preference
- `brightness` - Display brightness
- `lockout` or `childLock` - Control lockout
- `minCool`, `maxCool`, `minHeat`, `maxHeat` - Temperature limits
- `compressorDelay` - Minimum off time
- `filterHours` or `filterReset` - Filter maintenance
- `schedule` or `program` - Programming/schedules
- `swingMode` - Louver/swing control (if applicable)
- `turboMode` or `boost` - Boost/turbo feature
- `ecoMode` or `energySaver` - Energy-saving mode
- `sleepMode` - Sleep mode with gradual temperature adjustment
- `quietMode` - Quiet operation mode
- `display` - Display on/off

### 6. Missing Sensors/Entities

**Potential Additional Sensors**:
- Outdoor temperature sensor (if device supports)
- Return air temperature (if different from faceplate)
- Humidity sensor (if device has humidity sensing)
- Filter runtime/status (hours until replacement)
- Compressor runtime (for maintenance tracking)
- Error/fault code sensor
- Firmware version sensor
- Last command timestamp
- Connection quality/signal strength

**Potential Additional Binary Sensors**:
- Filter maintenance required
- System fault/error present
- Compressor running status
- Fan running status
- Heating active (different from HVAC action)
- Cooling active (different from HVAC action)
- Defrost cycle active (if applicable)

**Potential Additional Switches**:
- Display on/off
- Child lock
- Eco/energy-saving mode
- Quiet mode
- Temperature display units (°F/°C)

**Potential Additional Numbers**:
- Temperature offset/calibration
- Display brightness
- Minimum cool setpoint
- Maximum heat setpoint
- Compressor minimum off time

**Potential Additional Selects**:
- Display units (°F/°C)
- Swing/louver mode (if applicable)
- Operating mode presets

### 7. Advanced Features Not Implemented

**Scheduling/Programming**:
- The device may support programmable schedules (common in RV thermostats)
- Wake/sleep schedules
- Weekday/weekend different programs

**Multi-Zone Support**:
- As documented in ZONE_CONTROL_FINDINGS.md, zones 1, 2, etc. are not exposed
- No auto-discovery of available zones

**Diagnostics**:
- Detailed error codes
- Historical operating data
- Maintenance alerts
- System diagnostics

### 8. Location Service Limitations
The integration has a `set_location` service but:
- No way to query current location setting
- No sensor showing configured location
- No verification if location was set successfully

## Recommendations

### For Users
1. **Use the `query_device` service** to examine your device's full JSON response
2. **Check logs for**:
   - Additional top-level JSON keys beyond Z_sts, PRM, SN
   - Values in info[8], info[13], info[14]
   - Additional PRM parameter meanings
3. **Report findings** to help document device capabilities

### For Development
1. **Low-hanging fruit** - Expose info[8], [13], [14] with better labels
2. **Add sensors for**:
   - Each PRM parameter with interpretation
   - Firmware version (if available in JSON)
   - Filter status (if available)
3. **Investigate command types** beyond Get Status and Change
4. **Add configuration options** for:
   - Temperature calibration
   - Display preferences
   - Min/max temperature limits
5. **Implement zone auto-discovery** as outlined in ZONE_CONTROL_FINDINGS.md

### Investigation Commands
To help identify missing features, users should:

```yaml
# 1. Query device and examine full JSON
service: micro_air_easytouch.query_device
data:
  address: "AA:BB:CC:DD:EE:FF"

# 2. Check diagnostic sensor attributes
# Look at: Raw Info Array sensor attributes
# Look at: Parameters sensor attributes
```

Then check Home Assistant logs for:
- Any top-level JSON keys not mentioned above
- Actual values in info[8], info[13], info[14]
- All PRM parameter indices and values
- Array lengths (is info array always 16 items?)

## Conclusion

Based on code analysis, the integration currently uses:
- **16 of 16** info array values (3 marked as unknown)
- **2 of many** PRM parameters
- **3 of potentially many** top-level JSON keys
- **1 of potentially multiple** zones
- **2 command types** (Get Status, Change with limited parameters)

The most significant gaps are:
1. ⚠️ **Unknown info indices 8, 13, 14** - Could be important sensors
2. ⚠️ **Most PRM parameters undocumented** - May include useful settings
3. ⚠️ **Multi-zone not implemented** - Known limitation
4. ⚠️ **Potential additional JSON keys** - Need device query to discover
5. ⚠️ **Limited change parameters** - Many common features may be missing
6. ⚠️ **No scheduling support** - Common feature in thermostats

**Next Steps**: Users should run `query_device` and share complete device responses to help identify what additional data is available.

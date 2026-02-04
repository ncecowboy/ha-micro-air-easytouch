[![GitHub Release](https://img.shields.io/github/release/ncecowboy/ha-micro-air-easytouch.svg?style=flat-square)](https://github.com/k3vmcd/ha-micro-air-easytouch/releases)
[![License](https://img.shields.io/github/license/ncecowboy/ha-micro-air-easytouch.svg?style=flat-square)](LICENSE)
[![hacs](https://img.shields.io/badge/HACS-default-orange.svg?style=flat-square)](https://hacs.xyz)

# ha-micro-air-easytouch
Home Assistant Integration for the Micro-Air EasyTouch RV Thermostat

This integration implements a Home Assistant climate entity for basic control of your Micro-Air EasyTouch RV thermostat:

Core Features:
- Climate entity for HVAC control (Heat, Cool, Auto, Dry, Fan Only)
- Temperature monitoring via faceplate sensor
- Fan mode settings
- Temperature setpoint controls

Additional Sensors:
- **Temperature Sensor**: Current faceplate temperature reading
- **Current Mode**: Shows actual running mode (off, fan, cool, heat, etc.)
- **Current Fan Mode**: Displays the active fan setting
- **Serial Number**: Device serial number (diagnostic)
- **Raw Info Array**: Complete device status array with detailed attributes (diagnostic)
- **Parameters**: Device parameter array with interpreted values (diagnostic)

Additional Features:
- Device reboot button
- Service to configure device location for local weather display
- Service to query device for all available Bluetooth data (for troubleshooting and development)

## Diagnostic Sensors

The integration provides several diagnostic sensors that expose raw device data. These sensors are marked as diagnostic entities in Home Assistant and are hidden by default. They are useful for troubleshooting and understanding device behavior:

### Raw Info Array Sensor
This sensor shows the complete raw status array from the device as JSON. It includes detailed attributes that map each array index to its meaning:

- `info_0_autoHeat_sp`: Auto mode heat setpoint
- `info_1_autoCool_sp`: Auto mode cool setpoint
- `info_2_cool_sp`: Cool mode setpoint
- `info_3_heat_sp`: Heat mode setpoint
- `info_4_dry_sp`: Dry mode setpoint
- `info_5_dry_fan`: Dry mode fan setting
- `info_6_fan_mode`: Fan-only mode setting
- `info_7_cool_fan`: Cool mode fan setting
- `info_8_unknown`: Unknown value
- `info_9_auto_fan`: Auto mode fan setting
- `info_10_mode_num`: Mode number
- `info_11_heat_fan`: Heat mode fan setting
- `info_12_temperature`: Current temperature
- `info_13_unknown`: Unknown value
- `info_14_unknown`: Unknown value
- `info_15_current_mode`: Current operating mode

### Parameters Sensor
This sensor shows the device parameter array (PRM) with interpretation of known values:

- `param_0`, `param_1`, etc.: Raw parameter values
- `power_off_indicated`: True if parameter 7 is present (indicates power off state)
- `power_on_indicated`: True if parameter 15 is present (indicates power on state)

To view these diagnostic sensors in Home Assistant, go to **Settings** → **Devices & Services** → **Micro-Air EasyTouch** → your device, then click "Show disabled entities" or enable diagnostic entities in your dashboard.

## Troubleshooting: Query Device Bluetooth Data

The integration provides a `query_device` service that queries your thermostat for all available Bluetooth data and logs detailed information to help with troubleshooting or discovering additional capabilities.

### How to Use the Query Device Service

**Step 1: Enable Logging**

The query service outputs detailed information to Home Assistant logs, but you need to configure logging first. Add the following to your `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.micro_air_easytouch: info
```

After adding this configuration, restart Home Assistant for the changes to take effect.

**Step 2: Call the Service**

1. Go to **Developer Tools** → **Services** in Home Assistant
2. Select the service **Micro-Air EasyTouch: Query Device**
3. In the service data, provide your thermostat's MAC address:
   ```yaml
   address: "AA:BB:CC:DD:EE:FF"
   ```
   (Replace with your actual thermostat's MAC address, which you can find in Settings → Devices & Services → Micro-Air EasyTouch → Device Info)
4. Click **Call Service**

**Step 3: View the Output**

1. Go to **Settings** → **System** → **Logs**
2. Look for entries starting with `custom_components.micro_air_easytouch.services`
3. You should see detailed output including:
   - Raw device JSON response
   - Parsed data (temperature, modes, fan settings, etc.)
   - Raw info array values with indices
   - Device parameters (PRM)
   - Available Bluetooth UUIDs

**Example Output:**

The logs will show structured information like:
```
=== Querying device AA:BB:CC:DD:EE:FF for all available data ===
RAW DEVICE RESPONSE:
  Full JSON: { ... }

PARSED DATA:
  facePlateTemperature: 72.5
  mode_num: 2
  fan_mode_num: 128
  ...

RAW INFO ARRAY (Z_sts['0']):
  info[0] = 68
  info[1] = 78
  ...
```

### Common Issues

**No output in logs:**
- Verify you've added the logger configuration to `configuration.yaml`
- Ensure you restarted Home Assistant after adding the logger configuration
- Check that the MAC address matches your device exactly
- Ensure the thermostat is powered on and within Bluetooth range

**"No config entry found" error:**
- Make sure the integration is properly configured in Settings → Devices & Services
- Verify the MAC address format is correct (XX:XX:XX:XX:XX:XX with colons)

**"Could not find BLE device" error:**
- The thermostat may be out of Bluetooth range
- Try power cycling the thermostat
- Check if another device (like the manufacturer's mobile app) is currently connected to the thermostat

Known Limitations:
- The device responds slowly to commands - please wait a few seconds between actions
- When the unit is powered off from the device itself, this state is not reflected in Home Assistant
- Not all fan modes are settable in Home Assistant, "Cycled High" and "Cycled Low" are not available in Home Assistant - this is most likely due to limitations in the Home Assistant Climate entity
- Whenever the manufacturer mobile app connects to the device via bluetooth, Home Assistant will be temporarily disconnected and does not receive data

The integration works through Home Assistant's climate interface. You can control your thermostat through the Home Assistant UI or include it in automations, keeping in mind the device's response limitations.

## Important Upgrade Notice for v0.2.0

**⚠️ REQUIRED ACTION: Full Reinstallation Needed**

If you are upgrading from a version prior to 0.2.0, you must completely uninstall and reinstall the integration. This is due to significant internal changes that improve reliability and add new features.

To upgrade:
1. Remove the integration from Home Assistant (Settings → Devices & Services → Micro-Air EasyTouch → Delete)
2. Restart Home Assistant
3. Install the new version & restart Home Assistant
4. Add the integration again through the UI

## What's New in v0.2.0

- Now uses a Climate entity and is represented as an HVAC device in Home Assistant
- Enhanced Bluetooth connectivity reliability
- Improved error handling and recovery
- Added new service to configure device location

Please note that after upgrading and reconfiguring, you may need to wait a few minutes for all sensors to update and stabilize.

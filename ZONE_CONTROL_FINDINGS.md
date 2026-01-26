# Zone Control Data Analysis

## Summary
Yes, there is evidence of zone control capabilities in the Micro-Air EasyTouch thermostat data structure!

**UPDATE: Multi-zone support is now implemented!** The integration automatically detects and creates separate climate entities for each available zone.

## Implementation Status

### ✅ Completed Features
- **Automatic zone discovery**: Integration queries device and detects all available zones
- **Zone-specific climate entities**: Creates a separate climate entity for each zone
- **Zone-specific sensors**: Temperature, mode, and fan sensors for each zone
- **Zone-aware commands**: All control commands target the correct zone
- **Backward compatibility**: Single-zone devices work exactly as before with zone 0

### How It Works
When you add the integration, it:
1. Connects to your thermostat
2. Queries the device for available zones in the `Z_sts` data structure
3. Creates climate and sensor entities for each discovered zone
4. Labels multi-zone entities clearly (e.g., "Zone 1 Climate", "Zone 2 Temperature")

## Key Findings

### 1. Zone Status Data Structure (`Z_sts`)
The device's JSON response includes a `Z_sts` object that contains zone-based status information. Currently, the integration only accesses zone "0":

```python
status = json.loads(data)
info = status["Z_sts"]["0"]  # Currently only accessing zone 0
```

**Location in code:** `custom_components/micro_air_easytouch/micro_air_easytouch/parser.py:187`

### 2. Zone Parameter in Commands
All commands sent to the device include a `"zone"` parameter, currently hardcoded to `0`:

**Examples:**
- **Get Status**: `{"Type": "Get Status", "Zone": 0, ...}`
- **Change Settings**: `{"Type": "Change", "Changes": {"zone": 0, ...}}`
- **Device Reboot**: `{"Type": "Change", "Changes": {"zone": 0, "reset": " OK"}}`

**Locations in code:**
- `custom_components/micro_air_easytouch/climate.py` (lines 141, 263, 295, 324, 341)
- `custom_components/micro_air_easytouch/sensor.py` (line 88)
- `custom_components/micro_air_easytouch/services.py` (lines 76, 134)
- `custom_components/micro_air_easytouch/micro_air_easytouch/parser.py` (line 458)

### 3. Data Structure Design
The `Z_sts` dictionary structure suggests it was designed to handle multiple zones:
```json
{
  "Z_sts": {
    "0": [array of zone 0 status values],
    "1": [array of zone 1 status values],  // Potentially available
    "2": [array of zone 2 status values],  // Potentially available
    ...
  }
}
```

## Current Implementation
The integration now:
- **Auto-discovers all zones** from the `Z_sts` object
- **Queries each zone** independently
- **Creates separate climate entities** for each zone
- **Creates zone-specific sensors** (temperature, mode, fan)
- **Sends zone-targeted commands** for all operations
- **Falls back gracefully** to zone 0 if discovery fails

### Entity Naming
- **Single-zone** (zone 0 only): "EasyTouch Climate", "Temperature", etc.
- **Multi-zone**: "Zone 0 Climate", "Zone 1 Climate", "Zone 0 Temperature", "Zone 1 Temperature", etc.

## Multi-Zone Support Details

### Using Multi-Zone

If your thermostat has multiple zones, they will appear automatically after adding the integration:

**Climate Entities:**
- `climate.easytouch_zone_0_climate` - Zone 0 climate control
- `climate.easytouch_zone_1_climate` - Zone 1 climate control (if available)
- `climate.easytouch_zone_2_climate` - Zone 2 climate control (if available)

**Sensors (per zone):**
- Temperature sensor
- Current mode sensor
- Current fan mode sensor

**Device-Level Sensors** (shared, use zone 0 data):
- Serial number
- Raw info array
- Parameters

### Verification

To verify zones detected in your setup:
1. Add the integration in Home Assistant
2. Go to Settings → Devices & Services → Micro-Air EasyTouch
3. Click on your device
4. Count the number of climate entities - one per zone

Or check Home Assistant logs during setup:
```
INFO ... Discovered zones for device AA:BB:CC:DD:EE:FF: [0, 1, 2]
```

### Implementation Details

**Parser Changes:**
```python
# New method to discover zones
def get_available_zones(self, data: bytes) -> list[int]:
    """Discover available zones from device data."""
    status = json.loads(data)
    zones = []
    if "Z_sts" in status:
        for zone_key in status["Z_sts"].keys():
            zones.append(int(zone_key))
    return sorted(zones)

# Updated decrypt method accepts zone parameter
def decrypt(self, data: bytes, zone: int = 0) -> dict:
    """Parse and decode the device status data for a specific zone."""
    zone_key = str(zone)
    info = status["Z_sts"][zone_key]
    # ... rest of parsing
```

**Climate Entity Changes:**
- Added `zone` parameter to `__init__`
- Zone-specific unique_id and naming
- All commands use `self._zone` instead of hardcoded 0

**Sensor Entity Changes:**
- Added `zone` parameter to all sensor classes
- Zone-specific entities for temperature/mode/fan
- Device-level sensors use zone 0

### Backward Compatibility

Single-zone devices continue to work exactly as before:
- Zone 0 is the default
- Entity names unchanged for single-zone setups
- No breaking changes to existing configurations

## Hardware Capability
The Micro-Air EasyTouch product line may have different models:
- Single-zone models (most common in RVs)
- Multi-zone models (for larger RVs or multiple AC units)

The presence of zone-related data structures in the protocol suggests the firmware supports multi-zone configurations, even if not all hardware models utilize this capability.

## Troubleshooting

### No Multi-Zone Entities Appearing
If you have a multi-zone thermostat but only see zone 0:
1. Check Home Assistant logs for zone discovery messages
2. Try removing and re-adding the integration
3. Ensure your thermostat firmware supports multi-zone
4. Use the `query_device` service to verify zone data in raw response

### Manual Verification
You can still manually check for zones using the `query_device` service:

1. Enable logging in `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.micro_air_easytouch: info
```

2. Call the service:
```yaml
service: micro_air_easytouch.query_device
data:
  address: "AA:BB:CC:DD:EE:FF"
```

3. Check logs for `Z_sts` structure - look for keys like "0", "1", "2"

## Recommendations

### For Single-Zone Users
No action needed - integration works as before with zone 0 by default.

### For Multi-Zone Users
- Zones are automatically detected and configured
- Each zone gets independent climate and sensor entities
- Control each zone separately through Home Assistant
- Use automations to coordinate multi-zone HVAC control

## Conclusion
**Multi-zone support is now fully implemented!** The integration automatically detects and creates climate/sensor entities for all available zones. The `Z_sts` structure and the `zone` parameter in all commands are now fully utilized. Single-zone devices continue to work exactly as before.

# Zone Control Data Analysis

## Summary
Yes, there is evidence of zone control capabilities in the Micro-Air EasyTouch thermostat data structure!

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
The integration currently:
- Only queries zone 0 data
- Only sends commands to zone 0
- Does not check for additional zones in the `Z_sts` object
- Does not expose multiple zones as separate climate entities

## Potential Multi-Zone Support

### To Investigate Further
To determine if your specific thermostat supports multiple zones, you can use the existing `query_device` service:

1. Enable logging in `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.micro_air_easytouch: info
```

2. Call the service in Developer Tools → Services:
```yaml
service: micro_air_easytouch.query_device
data:
  address: "AA:BB:CC:DD:EE:FF"  # Your thermostat MAC address
```

3. Check the logs for the raw JSON response and look for additional zone keys in `Z_sts` (e.g., "1", "2", etc.)

### Implementation Considerations for Multi-Zone
If additional zones are detected, implementing multi-zone support would require:

1. **Discovery**: Check the `Z_sts` object for all available zone keys
2. **Entity Creation**: Create separate climate entities for each detected zone
   - `climate.easytouch_zone_0`
   - `climate.easytouch_zone_1`
   - etc.
3. **Zone-Specific Commands**: Modify all commands to target the specific zone
4. **Zone Identification**: Add zone information to device info and entity names

## Hardware Capability
The Micro-Air EasyTouch product line may have different models:
- Single-zone models (most common in RVs)
- Multi-zone models (for larger RVs or multiple AC units)

The presence of zone-related data structures in the protocol suggests the firmware supports multi-zone configurations, even if not all hardware models utilize this capability.

## Recommendations

1. **For Single-Zone Users**: No action needed - the current implementation works correctly
2. **For Multi-Zone Users**: 
   - Run the `query_device` service to check if zones 1, 2, etc. exist in your data
   - Report findings to the integration maintainer
   - Future enhancement could auto-detect and create entities for all available zones

## Example: How Multi-Zone Would Work
```python
# Future implementation concept
async def discover_zones(status_data):
    """Discover all available zones from Z_sts."""
    zones = []
    if "Z_sts" in status_data:
        for zone_id in status_data["Z_sts"].keys():
            zones.append(int(zone_id))
    return sorted(zones)

# Create one climate entity per zone
for zone in available_zones:
    entity = MicroAirEasyTouchClimate(data, mac_address, zone=zone)
    entities.append(entity)
```

## Conclusion
**Yes, zone control data exists in the protocol!** The `Z_sts` structure and the `zone` parameter in all commands clearly indicate zone control capability. However, the current integration only supports zone 0. Multi-zone support could be added in a future version if users have hardware that provides multiple zones.

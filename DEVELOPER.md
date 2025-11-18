# Developer Documentation

## Component Structure

The Zendure MQTT integration follows the standard Home Assistant custom component structure:

```
custom_components/zendure_mqtt/
├── __init__.py              # Component initialization
├── config_flow.py           # Configuration UI flow
├── const.py                 # Constants and configuration
├── manifest.json            # Component metadata
├── sensor.py                # Sensor platform implementation
├── strings.json             # UI strings
└── translations/
    └── en.json             # English translations
```

## Key Components

### 1. Configuration Flow (`config_flow.py`)

Implements the UI-based configuration with:
- MQTT broker connection validation
- Support for optional authentication
- Device model selection
- Unique ID generation to prevent duplicates

### 2. Sensor Platform (`sensor.py`)

Implements the MQTT sensor with:
- Automatic connection management
- Topic subscription: `zendure/{device_model}/#`
- Message handling and state updates
- Device information exposure
- Publish capability for writing to MQTT topics

### 3. Constants (`const.py`)

Defines:
- Domain identifier: `zendure_mqtt`
- Configuration keys
- Supported device models
- MQTT topic prefix

## Configuration Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `mqtt_host` | string | Yes | - | IP address of MQTT broker |
| `mqtt_port` | int | No | 1883 | Port number of MQTT broker |
| `mqtt_username` | string | No | "" | MQTT username (optional) |
| `mqtt_password` | string | No | "" | MQTT password (optional) |
| `device_model` | string | Yes | - | Device model selection |

## Supported Device Models

1. **hub1200** - HUB1200
2. **hub2000** - HUB2000
3. **aio2400** - AIO2400
4. **ace1500** - ACE1500
5. **hyper2000** - HYPER2000

## MQTT Topics

The component subscribes to all topics under:
```
zendure/{device_model}/#
```

Examples:
- `zendure/hub1200/status`
- `zendure/hub1200/battery/level`
- `zendure/hub2000/power/output`

## Entity Naming

Entities are named using the pattern:
```
sensor.zendure_{device_model}
```

Example: `sensor.zendure_hub1200`

## Device Information

Each configured device exposes:
- **Identifiers**: Unique identifier based on entry ID
- **Name**: "Zendure {MODEL}"
- **Manufacturer**: "Zendure"
- **Model**: Device model in uppercase

## State and Attributes

- **State**: Latest received MQTT message payload
- **Attributes**: All received MQTT topics and their values

## Publishing Messages

The sensor entity includes a `publish_mqtt()` method that can be used to publish messages to MQTT topics. This can be integrated with Home Assistant services or automations.

## Error Handling

The integration handles:
- Connection failures with proper error messages
- Invalid authentication
- MQTT disconnections with automatic reconnection
- Message parsing errors

## Logging

The component uses Python's logging module with the following loggers:
- `custom_components.zendure_mqtt.__init__`
- `custom_components.zendure_mqtt.config_flow`
- `custom_components.zendure_mqtt.sensor`

Enable debug logging in `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.zendure_mqtt: debug
```

## Testing

Use the validation scripts in `/tmp`:
- `validate_integration.py` - Validates file structure and basic requirements
- `test_structure.py` - Tests code structure and required components

## Future Enhancements

Potential improvements:
1. Add binary sensors for connection status
2. Implement switches for device control
3. Add support for device-specific attributes
4. Implement MQTT discovery
5. Add support for SSL/TLS connections
6. Create device-specific entities based on capabilities

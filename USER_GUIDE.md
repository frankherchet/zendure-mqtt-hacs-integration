# User Experience Guide

## Installation Process

### Via HACS (Recommended)
1. Open Home Assistant
2. Navigate to HACS → Integrations
3. Click the three dots menu → Custom repositories
4. Add: `https://github.com/frankherchet/zendure-mqtt-hacs-integration`
5. Category: Integration
6. Search for "Zendure MQTT"
7. Click Install
8. Restart Home Assistant

### Manual Installation
1. Download the repository
2. Copy `custom_components/zendure_mqtt/` to your Home Assistant's `config/custom_components/` directory
3. Restart Home Assistant

## Configuration Experience

### Step 1: Add Integration
Navigate to: **Settings → Devices & Services → Add Integration**

Search for: **Zendure MQTT**

### Step 2: Configure Connection
You'll see a form with the following fields:

```
┌─────────────────────────────────────────────┐
│  Configure Zendure MQTT                     │
├─────────────────────────────────────────────┤
│                                             │
│  Set up your Zendure device with MQTT      │
│                                             │
│  MQTT Broker IP Address: [____________]    │
│  Required                                   │
│                                             │
│  MQTT Broker Port: [1883___]               │
│  Optional (default: 1883)                   │
│                                             │
│  MQTT Username: [____________]              │
│  Optional                                   │
│                                             │
│  MQTT Password: [____________]              │
│  Optional                                   │
│                                             │
│  Device Model: [▼ Select model]            │
│  Options:                                   │
│    - hub1200     (Product ID: 73bkTV)      │
│    - hub2000     (Product ID: A8yh63)      │
│    - aio2400     (Product ID: yWF7hV)      │
│    - ace1500     (Product ID: 8bM93H)      │
│    - hyper2000   (Product ID: gDa3tb)      │
│                                             │
│  Device ID: [____________]                  │
│  Required (Your device's unique ID)         │
│                                             │
│  [Cancel]              [Submit]             │
└─────────────────────────────────────────────┘
```

### Step 3: Validation
The integration will:
- Test the MQTT broker connection
- Validate credentials (if provided)
- Validate device ID is not empty
- Show error if connection fails or device ID is invalid
- Create the integration if successful

### Possible Error Messages
- **"Failed to connect to MQTT broker"** - Check IP address, port, and that broker is running
- **"Device ID cannot be empty"** - You must enter a valid device ID
- **"Device is already configured"** - This device ID and model combination is already set up

## Post-Configuration Experience

### Device Created
After successful configuration, you'll see:

**Device Information:**
- Name: "Zendure HUB1200 (ABC123)" (includes device ID)
- Manufacturer: Zendure
- Model: HUB1200 (uppercase)
- Software Version: 73bkTV (Product ID)

**Entity Created:**
- Entity ID: `sensor.zendure_hub1200_abc123`
- State: Shows latest MQTT message
- Attributes: Device ID, Product ID, and all received MQTT topics

### Example Entity State
```yaml
state: "online"
attributes:
  device_id: "ABC123"
  product_id: "73bkTV"
  device_model: "hub1200"
  /73bkTV/ABC123/properties/report: "{...json data...}"
  /73bkTV/ABC123/status: "online"
  /73bkTV/ABC123/battery/level: "85"
  /73bkTV/ABC123/power/output: "120"
  friendly_name: "Zendure HUB1200 (ABC123)"
```

## Using the Integration

### In Lovelace Dashboard
Add a card to monitor your device:

```yaml
type: entities
entities:
  - entity: sensor.zendure_hub1200_abc123
title: My Zendure Device
```

### In Automations
Monitor device state changes:

```yaml
automation:
  - alias: "Low Battery Alert"
    trigger:
      - platform: state
        entity_id: sensor.zendure_hub1200_abc123
    condition:
      - condition: template
        value_template: "{{ state_attr('sensor.zendure_hub1200_abc123', '/73bkTV/ABC123/battery/level') | int < 20 }}"
    action:
      - service: notify.mobile_app
        data:
          message: "Zendure battery is low!"
```

### Viewing MQTT Topics
All subscribed topics appear as attributes on the sensor entity. You can view them in:
- Developer Tools → States → `sensor.zendure_hub1200_abc123`

## MQTT Topic Pattern

The integration subscribes to:
```
/{product_id}/{device_id}/properties/report
/{product_id}/{device_id}/#
```

Where `#` is a wildcard matching all sub-topics.

**Examples for HUB1200 with device ID "ABC123":**
- `/73bkTV/ABC123/properties/report` (main status topic)
- `/73bkTV/ABC123/status`
- `/73bkTV/ABC123/battery/level`
- `/73bkTV/ABC123/battery/voltage`
- `/73bkTV/ABC123/power/input`
- `/73bkTV/ABC123/power/output`

## Writing to MQTT Topics

While the sensor entity subscribes to read topics, the component includes publish capabilities that can be accessed through services or custom automations. The sensor entity has a `publish_mqtt(topic, payload)` method for advanced users.

## Troubleshooting

### Integration Not Appearing
- Ensure Home Assistant was restarted after installation
- Check logs: Settings → System → Logs
- Search for errors containing "zendure_mqtt"

### No Data Received
- Verify your Zendure device is publishing to MQTT
- Check the expected topic pattern: `/{product_id}/{device_id}/properties/report`
- Verify you entered the correct device ID during setup
- Use an MQTT client (like MQTT Explorer) to verify messages are being published
- Check Home Assistant logs for connection issues

### Connection Keeps Dropping
- Verify MQTT broker stability
- Check network connectivity
- Ensure credentials are correct
- Check MQTT broker logs for connection issues

## Removing the Integration

1. Navigate to: **Settings → Devices & Services**
2. Find "Zendure MQTT" integration
3. Click the three dots menu
4. Select "Delete"
5. Confirm deletion

The integration will cleanly disconnect from MQTT and remove all entities.

## Advanced Configuration

### Multiple Devices
You can add multiple Zendure devices:
1. Each device needs a separate integration entry
2. Use the same or different MQTT brokers
3. Each device will have its own entity

### Custom MQTT Topics
If your device uses different topic patterns, you may need to:
1. Fork the repository
2. Modify the topic pattern in `sensor.py`
3. Rebuild and reinstall

## Support

For issues, questions, or feature requests:
- Open an issue: https://github.com/frankherchet/zendure-mqtt-hacs-integration/issues
- Check existing documentation: README.md, DEVELOPER.md
- Review Home Assistant logs for detailed error messages

# Zendure MQTT HACS Integration

A Home Assistant Custom Component (HACS) for integrating Zendure devices via MQTT.

## Features

- 📡 Read and write MQTT topics for Zendure devices
- 🔧 Easy configuration through Home Assistant UI
- 🔐 Support for authenticated MQTT brokers
- 🎯 Support for multiple Zendure device models

## Supported Devices

- **HUB1200** - hub1200
- **HUB2000** - hub2000
- **AIO2400** - aio2400
- **ACE1500** - ace1500
- **HYPER2000** - hyper2000

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/frankherchet/zendure-mqtt-hacs-integration`
6. Select category: "Integration"
7. Click "Add"
8. Click "Install" on the Zendure MQTT card
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from GitHub
2. Copy the `custom_components/zendure_mqtt` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Zendure MQTT**
4. Fill in the required information:
   - **MQTT Broker IP Address**: The IP address of your MQTT broker
   - **MQTT Broker Port**: The port number (default: 1883)
   - **MQTT Username**: Username for authentication (optional, can be left empty)
   - **MQTT Password**: Password for authentication (optional, can be left empty)
   - **Device Model**: Select your Zendure device model from the dropdown

## MQTT Topics

The integration subscribes to topics following the pattern:
```
zendure/{device_model}/#
```

For example, for a HUB1200 device:
```
zendure/hub1200/#
```

## Usage

Once configured, the integration will:
- Create a sensor entity for your Zendure device
- Subscribe to relevant MQTT topics
- Display received data as sensor states and attributes
- Allow publishing messages to MQTT topics (via services or automation)

### Example Automation

```yaml
automation:
  - alias: "Monitor Zendure Device"
    trigger:
      - platform: state
        entity_id: sensor.zendure_hub1200
    action:
      - service: notify.notify
        data:
          message: "Zendure device state changed: {{ trigger.to_state.state }}"
```

## Troubleshooting

### Cannot Connect to MQTT Broker

- Verify the MQTT broker IP address is correct
- Check that the MQTT broker is running and accessible
- Ensure the port is correct (default: 1883)
- Verify username and password if authentication is required

### No Data Received

- Check that your Zendure device is publishing to the expected MQTT topics
- Verify the topic pattern: `zendure/{device_model}/#`
- Check Home Assistant logs for any error messages

## Support

For issues, feature requests, or questions, please open an issue on [GitHub](https://github.com/frankherchet/zendure-mqtt-hacs-integration/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

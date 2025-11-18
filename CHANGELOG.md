# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-18

### Added
- Initial release of Zendure MQTT integration for Home Assistant
- UI-based configuration flow for easy setup
- MQTT broker connection with optional authentication
- Device ID field for unique device identification
- Support for 5 Zendure device models with automatic product ID mapping:
  - HUB1200 (Product ID: 73bkTV)
  - HUB2000 (Product ID: A8yh63)
  - AIO2400 (Product ID: yWF7hV)
  - ACE1500 (Product ID: 8bM93H)
  - HYPER2000 (Product ID: gDa3tb)
- Sensor entity that subscribes to device MQTT topics
- Automatic MQTT connection management
- Device information exposure with product ID
- MQTT publish capability for sending messages
- HACS compatibility
- Comprehensive documentation

### Features
- Read MQTT topics from Zendure devices using proper topic structure: `/{product_id}/{device_id}/properties/report`
- Write MQTT topics to Zendure devices
- Configurable MQTT broker settings (IP, port, credentials)
- Device model selection during setup
- Device ID input for unique device identification
- Automatic product ID mapping based on device model
- Automatic topic subscription based on product ID and device ID: `/{product_id}/{device_id}/#`
- State and attribute tracking for all received messages
- Device ID, Product ID, and Model exposed as attributes
- Connection validation during configuration
- Unique device identification to prevent duplicates

[1.0.0]: https://github.com/frankherchet/zendure-mqtt-hacs-integration/releases/tag/v1.0.0

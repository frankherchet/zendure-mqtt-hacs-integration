# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-18

### Added
- Initial release of Zendure MQTT integration for Home Assistant
- UI-based configuration flow for easy setup
- MQTT broker connection with optional authentication
- Support for 5 Zendure device models:
  - HUB1200
  - HUB2000
  - AIO2400
  - ACE1500
  - HYPER2000
- Sensor entity that subscribes to device MQTT topics
- Automatic MQTT connection management
- Device information exposure
- MQTT publish capability for sending messages
- HACS compatibility
- Comprehensive documentation

### Features
- Read MQTT topics from Zendure devices
- Write MQTT topics to Zendure devices
- Configurable MQTT broker settings (IP, port, credentials)
- Device model selection during setup
- Automatic topic subscription based on device model
- State and attribute tracking for all received messages
- Connection validation during configuration
- Unique device identification to prevent duplicates

[1.0.0]: https://github.com/frankherchet/zendure-mqtt-hacs-integration/releases/tag/v1.0.0

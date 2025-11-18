"""Test the Zendure MQTT sensor."""
from unittest.mock import MagicMock, patch
import json

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.zendure_mqtt.const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_MODEL,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_PORT,
    CONF_MQTT_USERNAME,
    DOMAIN,
)
from custom_components.zendure_mqtt.sensor import ZendureMqttSensor

from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_sensor_setup(hass: HomeAssistant, mock_mqtt_client) -> None:
    """Test the sensor setup."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MQTT_HOST: "1.1.1.1",
            CONF_MQTT_PORT: 1883,
            CONF_MQTT_USERNAME: "test-user",
            CONF_MQTT_PASSWORD: "test-password",
            CONF_DEVICE_MODEL: "hub2000",
            CONF_DEVICE_ID: "test-device-id",
        },
    )
    entry.add_to_hass(hass)

    with patch("custom_components.zendure_mqtt.sensor.mqtt.Client", return_value=mock_mqtt_client):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("sensor.zendure_hub2000_test_device_id")
    assert state is not None
    assert state.name == "Zendure HUB2000 (test-device-id)"
    assert state.state == "unavailable"


async def test_sensor_update(hass: HomeAssistant, mock_mqtt_client) -> None:
    """Test the sensor update via MQTT."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_MQTT_HOST: "1.1.1.1",
            CONF_MQTT_PORT: 1883,
            CONF_MQTT_USERNAME: "test-user",
            CONF_MQTT_PASSWORD: "test-password",
            CONF_DEVICE_MODEL: "hub2000",
            CONF_DEVICE_ID: "test-device-id",
        },
    )
    entry.add_to_hass(hass)

    with patch("custom_components.zendure_mqtt.sensor.mqtt.Client", return_value=mock_mqtt_client):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Simulate connection
    mock_mqtt_client.on_connect(mock_mqtt_client, None, None, 0)
    
    # Simulate message
    msg = MagicMock()
    msg.topic = "/A8yh63/test-device-id/properties/report"
    msg.payload = json.dumps({"properties": {"electricLevel": 85}}).encode("utf-8")
    
    mock_mqtt_client.on_message(mock_mqtt_client, None, msg)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.zendure_hub2000_test_device_id")
    assert state is not None
    assert state.state == "85"
    assert state.attributes["electricLevel"] == 85

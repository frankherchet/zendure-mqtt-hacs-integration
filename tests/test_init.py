"""Test the Zendure MQTT initialization."""
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.zendure_mqtt.const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_MODEL,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_PORT,
    CONF_MQTT_USERNAME,
    DOMAIN,
)

from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_setup_unload_entry(hass: HomeAssistant, mock_mqtt_client) -> None:
    """Test setting up and unloading a config entry."""
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

    assert entry.state == ConfigEntryState.LOADED

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.NOT_LOADED

"""Test the Zendure MQTT config flow."""
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.zendure_mqtt.const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_MODEL,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_PORT,
    CONF_MQTT_USERNAME,
    DOMAIN,
)


async def test_form(hass: HomeAssistant, mock_mqtt_client) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "custom_components.zendure_mqtt.config_flow.validate_mqtt_connection",
        return_value=True,
    ), patch(
        "custom_components.zendure_mqtt.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MQTT_HOST: "1.1.1.1",
                CONF_MQTT_PORT: 1883,
                CONF_MQTT_USERNAME: "test-user",
                CONF_MQTT_PASSWORD: "test-password",
                CONF_DEVICE_MODEL: "hub2000",
                CONF_DEVICE_ID: "test-device-id",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Zendure HUB2000 (test-device-id)"
    assert result2["data"] == {
        CONF_MQTT_HOST: "1.1.1.1",
        CONF_MQTT_PORT: 1883,
        CONF_MQTT_USERNAME: "test-user",
        CONF_MQTT_PASSWORD: "test-password",
        CONF_DEVICE_MODEL: "hub2000",
        CONF_DEVICE_ID: "test-device-id",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(hass: HomeAssistant) -> None:
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.zendure_mqtt.config_flow.validate_mqtt_connection",
        return_value=False,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MQTT_HOST: "1.1.1.1",
                CONF_MQTT_PORT: 1883,
                CONF_MQTT_USERNAME: "test-user",
                CONF_MQTT_PASSWORD: "test-password",
                CONF_DEVICE_MODEL: "hub2000",
                CONF_DEVICE_ID: "test-device-id",
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_invalid_device_id(hass: HomeAssistant) -> None:
    """Test we handle invalid device id."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.zendure_mqtt.config_flow.validate_mqtt_connection",
        return_value=True,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MQTT_HOST: "1.1.1.1",
                CONF_MQTT_PORT: 1883,
                CONF_MQTT_USERNAME: "test-user",
                CONF_MQTT_PASSWORD: "test-password",
                CONF_DEVICE_MODEL: "hub2000",
                CONF_DEVICE_ID: "",
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "invalid_device_id"}

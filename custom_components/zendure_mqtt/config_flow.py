"""Config flow for Zendure MQTT integration."""
import logging
from typing import Any

import paho.mqtt.client as mqtt
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_MODEL,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_PORT,
    CONF_MQTT_USERNAME,
    DEFAULT_MQTT_PORT,
    DEVICE_MODELS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def validate_mqtt_connection(
    host: str, port: int, username: str | None, password: str | None
) -> bool:
    """Validate the MQTT connection."""
    try:
        client = mqtt.Client()

        if username and password:
            client.username_pw_set(username, password)
        elif username:
            client.username_pw_set(username)

        client.connect(host, port, 10)
        client.loop_start()
        client.loop_stop()
        client.disconnect()
        return True
    except Exception as err:
        _LOGGER.error("Failed to connect to MQTT broker: %s", err)
        return False


class ZendureMqttConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zendure MQTT."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate the MQTT connection
                mqtt_host = user_input[CONF_MQTT_HOST]
                mqtt_port = user_input.get(CONF_MQTT_PORT, DEFAULT_MQTT_PORT)
                mqtt_username = user_input.get(CONF_MQTT_USERNAME, "")
                mqtt_password = user_input.get(CONF_MQTT_PASSWORD, "")

                # Test connection
                is_valid = await self.hass.async_add_executor_job(
                    validate_mqtt_connection,
                    mqtt_host,
                    mqtt_port,
                    mqtt_username if mqtt_username else None,
                    mqtt_password if mqtt_password else None,
                )

                if not is_valid:
                    errors["base"] = "cannot_connect"
                else:
                    # Validate device ID is not empty
                    device_id = user_input.get(CONF_DEVICE_ID, "").strip()
                    if not device_id:
                        errors["base"] = "invalid_device_id"
                    else:
                        # Create a unique ID based on the device ID and model
                        await self.async_set_unique_id(
                            f"{device_id}_{user_input[CONF_DEVICE_MODEL]}"
                        )
                        self._abort_if_unique_id_configured()

                        return self.async_create_entry(
                            title=f"Zendure {user_input[CONF_DEVICE_MODEL].upper()} ({device_id})",
                            data=user_input,
                        )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show the configuration form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_MQTT_HOST): str,
                vol.Optional(CONF_MQTT_PORT, default=DEFAULT_MQTT_PORT): int,
                vol.Optional(CONF_MQTT_USERNAME, default=""): str,
                vol.Optional(CONF_MQTT_PASSWORD, default=""): str,
                vol.Required(CONF_DEVICE_MODEL): vol.In(DEVICE_MODELS),
                vol.Required(CONF_DEVICE_ID): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

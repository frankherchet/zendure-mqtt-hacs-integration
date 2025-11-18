"""Platform for Zendure MQTT sensor integration."""
import logging
from typing import Any

import paho.mqtt.client as mqtt

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_DEVICE_MODEL,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_PORT,
    CONF_MQTT_USERNAME,
    DEFAULT_MQTT_PORT,
    DOMAIN,
    TOPIC_PREFIX,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zendure MQTT sensor based on a config entry."""
    config = hass.data[DOMAIN][config_entry.entry_id]
    
    mqtt_host = config[CONF_MQTT_HOST]
    mqtt_port = config.get(CONF_MQTT_PORT, DEFAULT_MQTT_PORT)
    mqtt_username = config.get(CONF_MQTT_USERNAME)
    mqtt_password = config.get(CONF_MQTT_PASSWORD)
    device_model = config[CONF_DEVICE_MODEL]

    # Create MQTT client
    mqtt_client = mqtt.Client()
    
    if mqtt_username and mqtt_password:
        mqtt_client.username_pw_set(mqtt_username, mqtt_password)
    elif mqtt_username:
        mqtt_client.username_pw_set(mqtt_username)

    # Create sensor entity
    sensor = ZendureMqttSensor(
        mqtt_client,
        mqtt_host,
        mqtt_port,
        device_model,
        config_entry.entry_id,
    )

    async_add_entities([sensor], True)


class ZendureMqttSensor(SensorEntity):
    """Representation of a Zendure MQTT Sensor."""

    def __init__(
        self,
        mqtt_client: mqtt.Client,
        mqtt_host: str,
        mqtt_port: int,
        device_model: str,
        entry_id: str,
    ) -> None:
        """Initialize the sensor."""
        self._mqtt_client = mqtt_client
        self._mqtt_host = mqtt_host
        self._mqtt_port = mqtt_port
        self._device_model = device_model
        self._entry_id = entry_id
        self._attr_name = f"Zendure {device_model.upper()}"
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_sensor"
        self._state = None
        self._available = False
        self._attributes = {}

        # Set up MQTT callbacks
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_message = self._on_message
        self._mqtt_client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection."""
        if rc == 0:
            _LOGGER.info("Connected to MQTT broker")
            self._available = True
            # Subscribe to device topics
            topic = f"{TOPIC_PREFIX}/{self._device_model}/#"
            client.subscribe(topic)
            _LOGGER.info("Subscribed to topic: %s", topic)
        else:
            _LOGGER.error("Failed to connect to MQTT broker with code: %s", rc)
            self._available = False

    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        try:
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            _LOGGER.debug("Received message on topic %s: %s", topic, payload)
            
            # Store the latest message as state
            self._state = payload
            self._attributes[topic] = payload
            
            # Schedule an update
            if self.hass:
                self.schedule_update_ha_state()
        except Exception as err:
            _LOGGER.error("Error processing MQTT message: %s", err)

    def _on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection."""
        _LOGGER.warning("Disconnected from MQTT broker with code: %s", rc)
        self._available = False

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        
        # Connect to MQTT broker
        try:
            await self.hass.async_add_executor_job(
                self._mqtt_client.connect, self._mqtt_host, self._mqtt_port, 60
            )
            await self.hass.async_add_executor_job(self._mqtt_client.loop_start)
            _LOGGER.info("MQTT client started for %s", self._device_model)
        except Exception as err:
            _LOGGER.error("Failed to connect to MQTT broker: %s", err)

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from hass."""
        await super().async_will_remove_from_hass()
        
        # Disconnect from MQTT broker
        try:
            await self.hass.async_add_executor_job(self._mqtt_client.loop_stop)
            await self.hass.async_add_executor_job(self._mqtt_client.disconnect)
            _LOGGER.info("MQTT client stopped for %s", self._device_model)
        except Exception as err:
            _LOGGER.error("Failed to disconnect from MQTT broker: %s", err)

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self._state

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return self._attributes

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": f"Zendure {self._device_model.upper()}",
            "manufacturer": "Zendure",
            "model": self._device_model.upper(),
        }

    def publish_mqtt(self, topic: str, payload: str) -> bool:
        """Publish a message to an MQTT topic."""
        try:
            result = self._mqtt_client.publish(topic, payload)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as err:
            _LOGGER.error("Failed to publish MQTT message: %s", err)
            return False

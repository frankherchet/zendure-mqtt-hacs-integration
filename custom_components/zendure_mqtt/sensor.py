"""Platform for Zendure MQTT sensor integration."""
import logging
from typing import Any

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_MODEL,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_PORT,
    CONF_MQTT_USERNAME,
    DEFAULT_MQTT_PORT,
    DEVICE_PRODUCT_IDS,
    DOMAIN,
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
    device_id = config[CONF_DEVICE_ID]

    # Get the product ID for the device model
    product_id = DEVICE_PRODUCT_IDS.get(device_model)

    if mqtt is None:
        _LOGGER.error("paho-mqtt library is not installed")
        return

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
        device_id,
        product_id,
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
        device_id: str,
        product_id: str,
        entry_id: str,
    ) -> None:
        """Initialize the sensor."""
        self._mqtt_client = mqtt_client
        self._mqtt_host = mqtt_host
        self._mqtt_port = mqtt_port
        self._device_model = device_model
        self._device_id = device_id
        self._product_id = product_id
        self._entry_id = entry_id
        self._attr_name = f"Zendure {device_model.upper()} ({device_id})"
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
            # Subscribe to device report topic
            topic = f"/{self._product_id}/{self._device_id}/properties/report"
            client.subscribe(topic)
            _LOGGER.info("Subscribed to topic: %s", topic)

            # Subscribe to write reply topic for command responses
            write_reply_topic = f"/{self._product_id}/{self._device_id}/properties/write/reply"
            client.subscribe(write_reply_topic)
            _LOGGER.info("Subscribed to write reply topic: %s", write_reply_topic)

            # Also subscribe to all device topics for compatibility
            wildcard_topic = f"/{self._product_id}/{self._device_id}/#"
            client.subscribe(wildcard_topic)
            _LOGGER.info("Subscribed to wildcard topic: %s", wildcard_topic)
        else:
            _LOGGER.error("Failed to connect to MQTT broker with code: %s", rc)
            self._available = False

    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        try:
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            _LOGGER.debug("Received message on topic %s: %s", topic, payload)

            # Try to parse JSON payload
            try:
                import json
                from .properties import DEVICE_PROPERTIES, PACK_PROPERTIES, apply_conversion
                
                data = json.loads(payload)
                
                # Extract main fields
                if "messageId" in data:
                    self._attributes["messageId"] = data["messageId"]
                if "product" in data:
                    self._attributes["product"] = data["product"]
                if "deviceId" in data:
                    self._attributes["deviceId"] = data["deviceId"]
                if "timestamp" in data:
                    self._attributes["timestamp"] = data["timestamp"]
                
                # Parse device properties
                if "properties" in data and isinstance(data["properties"], dict):
                    for prop_key, prop_value in data["properties"].items():
                        if prop_key in DEVICE_PROPERTIES:
                            prop_def = DEVICE_PROPERTIES[prop_key]
                            # Apply conversion if specified
                            converted_value = apply_conversion(prop_value, prop_def["conversion"])
                            self._attributes[prop_key] = converted_value
                        else:
                            # Store unknown properties as-is
                            self._attributes[prop_key] = prop_value
                
                # Parse battery pack data
                if "packData" in data and isinstance(data["packData"], list):
                    self._attributes["pack_count"] = len(data["packData"])
                    for pack_idx, pack in enumerate(data["packData"]):
                        if isinstance(pack, dict) and "sn" in pack:
                            pack_sn = pack["sn"]
                            pack_prefix = f"pack_{pack_sn}"
                            
                            # Store pack serial number
                            self._attributes[f"{pack_prefix}_sn"] = pack_sn
                            
                            # Parse pack properties
                            for pack_prop_key, pack_prop_value in pack.items():
                                if pack_prop_key == "sn":
                                    continue  # Already stored
                                
                                if pack_prop_key in PACK_PROPERTIES:
                                    pack_prop_def = PACK_PROPERTIES[pack_prop_key]
                                    # Apply conversion if specified
                                    converted_value = apply_conversion(
                                        pack_prop_value, 
                                        pack_prop_def["conversion"]
                                    )
                                    self._attributes[f"{pack_prefix}_{pack_prop_key}"] = converted_value
                                else:
                                    # Store unknown pack properties as-is
                                    self._attributes[f"{pack_prefix}_{pack_prop_key}"] = pack_prop_value
                
                # Set state to a summary or status if available
                if "properties" in data and isinstance(data["properties"], dict):
                    # Use electricLevel (battery level) as state if available
                    if "electricLevel" in data["properties"]:
                        self._state = str(data["properties"]["electricLevel"])
                    # Otherwise use packState
                    elif "packState" in data["properties"]:
                        pack_state = data["properties"]["packState"]
                        state_map = {0: "idle", 1: "charging", 2: "discharging"}
                        self._state = state_map.get(pack_state, str(pack_state))
                    else:
                        self._state = "online"
                else:
                    self._state = "online"
                    
            except json.JSONDecodeError:
                # Not JSON, store as raw payload
                _LOGGER.debug("Payload is not JSON, storing as raw")
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
        attributes = {
            "device_id": self._device_id,
            "product_id": self._product_id,
            "device_model": self._device_model,
        }
        # Add all received MQTT topics as attributes
        attributes.update(self._attributes)
        return attributes

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"Zendure {self._device_model.upper()} ({self._device_id})",
            "manufacturer": "Zendure",
            "model": self._device_model.upper(),
            "sw_version": self._product_id,
        }

    def publish_mqtt(self, topic: str, payload: str) -> bool:
        """Publish a message to an MQTT topic."""
        try:
            result = self._mqtt_client.publish(topic, payload)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as err:
            _LOGGER.error("Failed to publish MQTT message: %s", err)
            return False

    def write_property(self, properties: dict[str, Any]) -> bool:
        """Write properties to device using the command topic.
        
        Args:
            properties: Dictionary of property names and values to write
            
        Returns:
            True if message was published successfully
            
        Example:
            sensor.write_property({"outputLimit": 1000, "socSet": 900})
        """
        import json
        
        try:
            # Build command topic
            command_topic = f"iot/{self._product_id}/{self._device_id}/properties/write"
            
            # Build payload with properties
            payload = {
                "properties": properties
            }
            
            # Publish command
            result = self._mqtt_client.publish(command_topic, json.dumps(payload))
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                _LOGGER.info("Published write command to %s: %s", command_topic, properties)
                return True
            else:
                _LOGGER.error("Failed to publish write command, rc=%s", result.rc)
                return False
                
        except Exception as err:
            _LOGGER.error("Failed to write property: %s", err)
            return False

"""Constants for the Zendure MQTT integration."""

DOMAIN = "zendure_mqtt"

# Configuration keys
CONF_MQTT_HOST = "mqtt_host"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USERNAME = "mqtt_username"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_DEVICE_MODEL = "device_model"

# Default values
DEFAULT_MQTT_PORT = 1883

# Supported device models
MODEL_HUB1200 = "hub1200"
MODEL_HUB2000 = "hub2000"
MODEL_AIO2400 = "aio2400"
MODEL_ACE1500 = "ace1500"
MODEL_HYPER2000 = "hyper2000"

DEVICE_MODELS = [
    MODEL_HUB1200,
    MODEL_HUB2000,
    MODEL_AIO2400,
    MODEL_ACE1500,
    MODEL_HYPER2000,
]

# MQTT Topics
TOPIC_PREFIX = "zendure"

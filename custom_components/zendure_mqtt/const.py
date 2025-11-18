"""Constants for the Zendure MQTT integration."""

DOMAIN = "zendure_mqtt"

# Configuration keys
CONF_MQTT_HOST = "mqtt_host"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USERNAME = "mqtt_username"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_DEVICE_MODEL = "device_model"
CONF_DEVICE_ID = "device_id"

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

# Product ID mapping for each device model
DEVICE_PRODUCT_IDS = {
    MODEL_HUB1200: "73bkTV",
    MODEL_HUB2000: "A8yh63",
    MODEL_AIO2400: "yWF7hV",
    MODEL_ACE1500: "8bM93H",
    MODEL_HYPER2000: "gDa3tb",
}

# MQTT Topics
TOPIC_PREFIX = "zendure"
MQTT_TOPIC_REPORT = "/{product_id}/{device_id}/properties/report"
MQTT_TOPIC_WRITE = "iot/{product_id}/{device_id}/properties/write"
MQTT_TOPIC_WRITE_REPLY = "/{product_id}/{device_id}/properties/write/reply"

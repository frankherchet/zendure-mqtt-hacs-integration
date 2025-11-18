"""Global fixtures for Zendure MQTT integration tests."""
from unittest.mock import MagicMock, patch

import pytest

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    yield

@pytest.fixture
def mock_mqtt_client():
    """Mock the paho.mqtt.client.Client."""
    with patch("paho.mqtt.client.Client") as mock_client:
        client_instance = mock_client.return_value
        client_instance.connect.return_value = 0
        yield client_instance

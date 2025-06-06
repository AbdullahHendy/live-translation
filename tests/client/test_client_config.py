import pytest
from live_translation.client.config import Config


@pytest.fixture
def default_config():
    return Config(server_uri="ws://localhost:8765")


def test_config_fields(default_config):
    """Verify client config default fields."""
    assert default_config.SERVER_URI == "ws://localhost:8765"
    assert default_config.CHUNK_SIZE == 640
    assert default_config.SAMPLE_RATE == 16000
    assert default_config.CHANNELS == 1
    assert default_config.CODEC == "opus"


def test_config_validate():
    """Should raise ValueError for invalid WebSocket URI."""
    invalid_configs = [
        {"server_uri": "http://localhost:8765"},
        {"server_uri": "ws://localhost:8765", "codec": "invalid_codec"},
    ]

    for config in invalid_configs:
        with pytest.raises(ValueError):
            # Try to instantiate Config with the invalid configuration
            Config(**config)


def test_config_immutable_fields(default_config):
    """Ensure critical audio config fields cannot be modified."""
    with pytest.raises(AttributeError):
        default_config.SAMPLE_RATE = 8000
        default_config.CHUNK_SIZE = 1280
        default_config.CHANNELS = 2

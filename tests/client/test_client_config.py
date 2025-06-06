import pytest
from live_translation.client.config import Config


@pytest.fixture
def config():
    return Config(server_uri="ws://localhost:8765")


def test_config_fields(config):
    """Verify client config default fields."""
    assert config.SERVER_URI == "ws://localhost:8765"
    assert config.CHUNK_SIZE == 640
    assert config.SAMPLE_RATE == 16000
    assert config.CHANNELS == 1


def test_config_rejects_invalid_uri():
    """Should raise ValueError for invalid WebSocket URI."""
    with pytest.raises(ValueError, match="must start with 'ws://'"):
        Config(server_uri="http://localhost:8765")


def test_config_immutable_fields(config):
    """Ensure critical audio config fields cannot be modified."""
    with pytest.raises(AttributeError):
        config.SAMPLE_RATE = 8000
        config.CHUNK_SIZE = 1280
        config.CHANNELS = 2

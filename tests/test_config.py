import pytest
from live_translation.config import Config


@pytest.fixture
def default_config():
    """Fixture to create a default Config instance."""
    return Config()


def test_config_defaults(default_config):
    """Test if Config initializes with default values."""
    assert default_config.DEVICE == "cpu"
    assert default_config.WHISPER_MODEL == "base"
    assert default_config.TRANS_MODEL == "Helsinki-NLP/opus-mt"
    assert default_config.SRC_LANG == "en"
    assert default_config.TGT_LANG == "es"
    assert default_config.OUTPUT == "print"
    assert default_config.WS_PORT is None
    assert default_config.SILENCE_THRESHOLD == 65
    assert default_config.VAD_AGGRESSIVENESS == 8
    assert default_config.MAX_BUFFER_DURATION == 7
    assert default_config.TRANSCRIBE_ONLY is False


def test_config_modifiable_attributes():
    """Test if mutable attributes can be changed."""
    cfg = Config(
        device="cpu",
        whisper_model="tiny",
        trans_model="Helsinki-NLP/opus-mt",
        src_lang="en",
        tgt_lang="hi",
        output="websocket",
        ws_port=8080,
        silence_threshold=70,
        vad_aggressiveness=5,
        max_buffer_duration=10,
        transcribe_only=True,
    )
    assert cfg.DEVICE == "cpu"
    assert cfg.WHISPER_MODEL == "tiny"
    assert cfg.TRANS_MODEL == "Helsinki-NLP/opus-mt"
    assert cfg.SRC_LANG == "en"
    assert cfg.TGT_LANG == "hi"
    assert cfg.OUTPUT == "websocket"
    assert cfg.WS_PORT == 8080
    assert cfg.SILENCE_THRESHOLD == 70
    assert cfg.VAD_AGGRESSIVENESS == 5
    assert cfg.MAX_BUFFER_DURATION == 10
    assert cfg.TRANSCRIBE_ONLY is True


def test_config_immutable_attributes():
    """Test if immutable attributes remain unchanged."""
    cfg = Config()
    with pytest.raises(AttributeError):
        # @property immutables
        cfg.CHUNK_SIZE = 1024
        cfg.SAMPLE_RATE = 44100
        cfg.CHANNELS = 2
        cfg.ENQUEUE_THRESHOLD = 2
        cfg.TRIM_FACTOR = 0.5
        cfg.SOFT_SILENCE_THRESHOLD = 32


def test_config_validate():
    """Test if Config validates the parameters during initialization."""
    invalid_configs = [
        {"device": "gpu"},
        {"whisper_model": "super"},
        {"trans_model": "Helsinki-NLP/random"},
        {"output": "random"},
        {"vad_aggressiveness": 10},
        {"max_buffer_duration": 4},
    ]

    for config in invalid_configs:
        with pytest.raises(ValueError):
            # Try to instantiate Config with the invalid configuration
            Config(**config)

from unittest import mock
import pytest
from live_translation.server.config import Config


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
    assert default_config.LOG is None
    assert default_config.WS_PORT == 8765
    assert default_config.SILENCE_THRESHOLD == 2
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
        log="print",
        ws_port=8080,
        silence_threshold=4,
        vad_aggressiveness=5,
        max_buffer_duration=10,
        transcribe_only=True,
    )
    assert cfg.DEVICE == "cpu"
    assert cfg.WHISPER_MODEL == "tiny"
    assert cfg.TRANS_MODEL == "Helsinki-NLP/opus-mt"
    assert cfg.SRC_LANG == "en"
    assert cfg.TGT_LANG == "hi"
    assert cfg.LOG == "print"
    assert cfg.WS_PORT == 8080
    assert cfg.SILENCE_THRESHOLD == 4
    assert cfg.VAD_AGGRESSIVENESS == 5
    assert cfg.MAX_BUFFER_DURATION == 10
    assert cfg.TRANSCRIBE_ONLY is True


def test_config_immutable_defaults():
    cfg = Config()
    assert cfg.CHUNK_SIZE == 640
    assert cfg.SAMPLE_RATE == 16000
    assert cfg.CHANNELS == 1
    assert cfg.ENQUEUE_THRESHOLD == 1
    assert cfg.TRIM_FACTOR == 0.75
    assert cfg.SOFT_SILENCE_THRESHOLD == 0.5


def test_config_immutable_attributes():
    """Test if immutable attributes remain unchanged."""
    cfg = Config()
    with pytest.raises(AttributeError):
        # @property immutables
        cfg.CHUNK_SIZE = 1280
        cfg.SAMPLE_RATE = 44100
        cfg.CHANNELS = 2
        cfg.ENQUEUE_THRESHOLD = 2
        cfg.TRIM_FACTOR = 0.5
        cfg.SOFT_SILENCE_THRESHOLD = 1.5


def test_config_validate():
    """Test if Config validates the parameters during initialization."""
    invalid_configs = [
        {"device": "gpu"},
        {"whisper_model": "super"},
        # transcibe_only=True to avoid early ValueError on RepositoryNotFoundError
        {"trans_model": "Helsinki-NLP/random", "transcribe_only": True},
        {"trans_model": "Helsinki-NLP/random"},
        {"log": "random"},
        {"vad_aggressiveness": 10},
        {"max_buffer_duration": 4},
        {"silence_threshold": 1},
    ]

    for config in invalid_configs:
        with pytest.raises(ValueError):
            # Try to instantiate Config with the invalid configuration
            Config(**config)


def test_config_invalid_ws_port():
    with pytest.raises(ValueError, match="WebSocket port is required"):
        Config(ws_port=None)


def test_config_cuda_not_available(monkeypatch):
    monkeypatch.setattr("torch.cuda.is_available", lambda: False)
    with pytest.raises(ValueError, match="cuda' device is not available"):
        Config(device="cuda")


def test_config_transcribe_only_skips_model_check():
    """Ensure _validate skips Hugging Face check when transcribe_only=True"""
    # patch hf_hub.model_info to explode if called (to prove it's skipped)
    with mock.patch(
        "huggingface_hub.model_info", side_effect=RuntimeError("should not be called")
    ):
        Config(transcribe_only=True)


def test_general_exception():
    with mock.patch(
        "live_translation.server.config.hf_hub.model_info"
    ) as mock_model_info:
        mock_model_info.side_effect = Exception("network timeout")

        with pytest.raises(
            ValueError,
            match="🚨 An error when verifying the translation model: network timeout",
        ):
            Config(transcribe_only=False)

import numpy as np
import pytest
import wave
from live_translation._audio._codec import OpusCodec
from live_translation.server.config import Config


@pytest.fixture
def config():
    """Fixture to provide a default configuration."""
    return Config()


@pytest.fixture
def opus_codec(config):
    """Fixture to provide an instance of OpusCodec."""
    return OpusCodec(config)


@pytest.fixture
def real_speech():
    """Load a real speech sample."""
    with wave.open("tests/audio_samples/sample.wav", "rb") as wf:
        num_channels = wf.getnchannels()
        frame_rate = wf.getframerate()
        num_frames = wf.getnframes()

        assert frame_rate == 16000, f"Expected 16kHz, got {frame_rate}Hz"
        assert num_channels == 1, f"Expected mono, got {num_channels} channels"

        raw_audio = wf.readframes(num_frames)
        return np.frombuffer(raw_audio, dtype=np.int16)


def test_opus_codec_full_wav_roundtrip(opus_codec, config, real_speech):
    """Test OpusCodec on full real-speech wav."""
    # NOTE: This test doesn't verify "how it sounds", but checks if Opus can
    # encode/decode without errors and with proper compression.
    # For actual sound quality, look into PESQ or other audio quality metrics.
    total_samples = len(real_speech)

    encoded_size = 0

    for i in range(0, total_samples - config._CHUNK_SIZE + 1, config._CHUNK_SIZE):
        chunk = real_speech[i : i + config._CHUNK_SIZE]
        encoded = opus_codec.encode(chunk.tobytes())
        decoded = opus_codec.decode(encoded)

        encoded_size += len(encoded)

        decoded_array = np.frombuffer(decoded, dtype=np.int16)

        assert len(decoded_array) == len(chunk), (
            f"Decoded length {len(decoded_array)} does not match \
            original chunk length {len(chunk)}"
        )

    original_size = len(real_speech.tobytes())
    reduction_ratio = 1 - (encoded_size / original_size)

    assert reduction_ratio > 0.9, (
        "Opus should compress audio significantly (more than 90%)"
    )

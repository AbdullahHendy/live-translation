import pytest
import numpy as np
import torchaudio
from live_translation._audio._vad import VoiceActivityDetector
from live_translation.server.config import Config


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def vad(config):
    """Initialize VAD with real model (downloads once)."""
    return VoiceActivityDetector(config)


@pytest.fixture
def real_speech():
    """Load a real speech sample and return all chunks."""
    waveform, _ = torchaudio.load("tests/audio_samples/sample.wav")
    return waveform[0].numpy().astype(np.float32)


@pytest.fixture
def real_silence():
    """Generate real silence (512 samples)."""
    return np.zeros(512, dtype=np.float32)


def test_vad_detects_speech(vad, real_speech):
    """Test if VAD detects speech correctly using real speech."""
    chunk_size = 640
    detected_speech = False

    # Loop through the entire file in 640-sample chunks
    for i in range(0, len(real_speech) - chunk_size + 1, chunk_size):
        chunk = real_speech[i : i + chunk_size]
        if vad.is_speech(chunk):
            detected_speech = True
            print(f"speech detected at {i / 16} ms")
            break

    assert detected_speech, "VAD should detect speech in at least one chunk"


def test_vad_detects_silence(vad, real_silence):
    """Test if VAD detects silence correctly."""
    result = vad.is_speech(real_silence)
    assert result is False, "VAD should detect silence"


def test_vad_non_float32(vad):
    """Ensure VAD raises ValueError if input is not float32."""
    fake_audio = np.zeros(512, dtype=np.int16)  # wrong dtype

    with pytest.raises(ValueError, match="must be of type float32"):
        vad.is_speech(fake_audio)


def test_vad_slice_audio(vad, real_speech):
    """Test if audio slicing works (length focused test)."""
    # Short audio case
    short_audio = np.arange(400, dtype=np.float32)  # 400 samples
    chunks = vad._slice_audio(short_audio, vad_frame_size=512)
    assert len(chunks) == 1, "Should be one chunk for audio less than 512 samples"
    assert len(chunks[0]) == 512, "Chunk should be padded to 512 samples"

    # Exactly 512 samples
    exact_audio = np.arange(512, dtype=np.float32)  # 512 samples
    chunks = vad._slice_audio(exact_audio, vad_frame_size=512)
    assert len(chunks) == 1, "Should be one chunk for exactly 512 samples"
    assert len(chunks[0]) == 512, "Chunk should be exactly 512 samples"

    # Long audio case (not exact multiple of 512)
    long_audio_not_mult = np.arange(640, dtype=np.float32)  # 640 samples
    chunks = vad._slice_audio(long_audio_not_mult, vad_frame_size=512)
    assert len(chunks) == 2, "Should be two chunks for audio longer than 640  samples"
    assert len(chunks[0]) == 512, "First chunk should be 512 samples"
    assert len(chunks[1]) == 512, "Second chunk should be 512 samples"

    # Long audio case (exact multiple of 512)
    long_audio_mult = np.arange(1024, dtype=np.float32)  # 1024 samples
    chunks = vad._slice_audio(long_audio_mult, vad_frame_size=512)
    assert len(chunks) == 2, "Should be two chunks for audio longer than 1024 samples"
    assert len(chunks[0]) == 512, "First chunk should be 512 samples"
    assert len(chunks[1]) == 512, "Second chunk should be 512 samples"

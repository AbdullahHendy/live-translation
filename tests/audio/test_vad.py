import pytest
import numpy as np
import torchaudio
from live_translation._audio._vad import VoiceActivityDetector


@pytest.fixture
def vad():
    """Initialize VAD with real model (downloads once)."""
    return VoiceActivityDetector(aggressiveness=5)


@pytest.fixture
def real_speech():
    """Load a real speech sample and return all chunks of 512 samples."""
    waveform, _ = torchaudio.load("tests/audio_samples/sample.wav")
    return waveform[0].numpy().astype(np.float32)


@pytest.fixture
def real_silence():
    """Generate real silence (512 samples)."""
    return np.zeros(512, dtype=np.float32)


def test_vad_detects_speech(vad, real_speech):
    """Test if VAD detects speech correctly using real speech."""
    chunk_size = 512
    detected_speech = False

    # Loop through the entire file in 512-sample chunks
    for i in range(0, len(real_speech) - chunk_size + 1, chunk_size):
        chunk = real_speech[i : i + chunk_size]
        if vad.is_speech(chunk, sample_rate=16000):
            detected_speech = True
            print(f"speech detected at {i / 16} ms")
            break

    assert detected_speech, "VAD should detect speech in at least one chunk"


def test_vad_detects_silence(vad, real_silence):
    """Test if VAD detects silence correctly."""
    result = vad.is_speech(real_silence, sample_rate=16000)
    assert result is False, "VAD should detect silence"

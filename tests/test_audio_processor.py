import pytest
import numpy as np
import wave
import multiprocessing as mp
import threading
import time
from live_translation._audio._processor import AudioProcessor
from live_translation.config import Config


@pytest.fixture
def audio_queue():
    queue = mp.Queue()
    yield queue
    queue.cancel_join_thread()
    queue.close()


@pytest.fixture
def processed_queue():
    queue = mp.Queue()
    yield queue
    queue.cancel_join_thread()
    queue.close()


@pytest.fixture
def stop_event():
    return threading.Event()


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def real_speech():
    """Load a real speech sample."""
    with wave.open("tests/audio_samples/sample.wav", "rb") as wf:
        num_channels = wf.getnchannels()
        frame_rate = wf.getframerate()
        num_frames = wf.getnframes()

        assert frame_rate == 16000, f"Expected 16kHz sample rate, got {frame_rate}Hz"
        assert num_channels == 1, f"Expected mono audio, got {num_channels} channels"

        # Read raw PCM data
        raw_audio = wf.readframes(num_frames)
        audio_data = np.frombuffer(raw_audio, dtype=np.int16)

    return audio_data


def test_audio_processor_pipeline(
    audio_queue, processed_queue, stop_event, config, real_speech
):
    """Send audio to audio_queue and check processed_queue."""

    # Send audio to `audio_queue`
    chunk_size = 512
    for i in range(0, len(real_speech) - chunk_size + 1, chunk_size):
        chunk = real_speech[i : i + chunk_size]
        audio_queue.put(chunk)

    processor = AudioProcessor(audio_queue, processed_queue, stop_event, config)
    processor.start()

    time.sleep(10)

    assert not processed_queue.empty(), (
        "Processed queue should contain VAD-filtered audio"
    )
    processed_data = processed_queue.get()

    stop_event.set()
    processor.join(timeout=3)
    processor._cleanup()

    if processor.is_alive():
        processor.terminate()

    assert (
        isinstance(processed_data, np.ndarray) and processed_data.dtype == np.float32
    ), "❌ Processed audio format is incorrect!"

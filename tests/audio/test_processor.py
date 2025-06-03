from unittest import mock
import pytest
import numpy as np
import wave
import multiprocessing as mp
import time
from live_translation._audio._processor import AudioProcessor
from live_translation.server.config import Config


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
    return mp.Event()


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

    chunk_size = 512
    for i in range(0, len(real_speech) - chunk_size + 1, chunk_size):
        chunk = real_speech[i : i + chunk_size]
        audio_queue.put(chunk)

    processor = AudioProcessor(audio_queue, processed_queue, stop_event, config)
    processor.start()

    timeout = 25  # Audio file 'sample_long.wav' is about 17 seconds long
    poll_interval = 0.1
    waited = 0

    # Allow for the whole audio to be processed (audio_queue must be empty)
    # This allows for coverage of more complex scenarios like silence detection and
    # trimming long buffers.
    # The test sample has more than SILENCE_THRESHOLD towards the end for silence
    # detection coverage.
    # The test sample has more than MAX_BUFFER_DURATION for buffer trimming coverage.
    while (not audio_queue.empty() or processed_queue.empty()) and waited < timeout:
        time.sleep(poll_interval)
        waited += poll_interval

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
    ), "Processed audio format is incorrect!"


def test_audio_processor_empty_queue(audio_queue, processed_queue, stop_event, config):
    """Test processor with an empty audio queue."""
    processor = AudioProcessor(audio_queue, processed_queue, stop_event, config)
    processor.start()

    # Allow some time for the processor to run so that it gets to the point of checking
    # the empty queue to cover the `except queue.Empty:` case in the processor code.
    time.sleep(5)

    stop_event.set()
    processor.join(timeout=3)
    processor._cleanup()

    if processor.is_alive():
        processor.terminate()

    assert processed_queue.empty(), "Processed queue should be empty for no input"


def test_audio_processor_cleanup_exception(capfd):
    """Test _cleanup handles exceptions during queue close."""
    config = Config()
    processor = AudioProcessor(None, None, None, config)

    # Replace processed_queue with a mock that raises on close
    processor._processed_queue = mock.Mock()
    processor._processed_queue.close.side_effect = RuntimeError("fail on close")

    # Should not raise
    processor._cleanup()

    out, _ = capfd.readouterr()
    assert "🚨 AudioProcessor Cleanup Error: fail on close" in out


def test_audio_processor_seconds_to_chunks(config):
    """Test that seconds-to-chunks conversion is accurate."""
    processor = AudioProcessor(None, None, None, config)

    config._CHUNK_SIZE = 512
    config._SAMPLE_RATE = 16000
    seconds = 1
    expected_chunks = int(round(seconds / (512 / 16000)))
    actual_chunks = processor._seconds_to_chunks(seconds)
    assert actual_chunks == expected_chunks

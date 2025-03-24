import pytest
import numpy as np
import multiprocessing as mp
import threading
import time
from unittest.mock import MagicMock, patch
from live_translation._audio._recorder import AudioRecorder
from live_translation.config import Config


@pytest.fixture
def audio_queue():
    queue = mp.Queue()
    yield queue
    queue.close()


@pytest.fixture
def stop_event():
    return threading.Event()


@pytest.fixture
def config():
    return Config()


@patch("live_translation._audio._recorder.pyaudio.PyAudio")
def test_audio_recorder_initialization(mock_pyaudio, audio_queue, stop_event, config):
    """Test if AudioRecorder initializes correctly."""

    mock_stream = MagicMock()
    mock_pyaudio.return_value.open.return_value = mock_stream
    mock_stream.is_active.return_value = True

    recorder = AudioRecorder(audio_queue, stop_event, config)

    assert recorder._audio_queue is audio_queue
    assert recorder._stop_event is stop_event
    assert recorder._cfg is config
    assert recorder._pyaudio_instance is not None
    assert recorder._stream is not None
    assert recorder._stream.is_active()

    recorder._cleanup()


@patch("live_translation._audio._recorder.pyaudio.PyAudio")
def test_audio_recorder(mock_pyaudio, audio_queue, stop_event, config):
    """Test AudioRecorder correctly captures audio and stops cleanly."""
    mock_stream = MagicMock()
    mock_pyaudio.return_value.open.return_value = mock_stream
    mock_stream.read.return_value = np.zeros(
        config.CHUNK_SIZE, dtype=np.int16
    ).tobytes()

    recorder = AudioRecorder(audio_queue, stop_event, config)
    recorder.start()

    time.sleep(1)

    assert not audio_queue.empty()
    audio_data = audio_queue.get()

    stop_event.set()
    recorder.join(timeout=3)

    recorder._cleanup()

    audio_queue.cancel_join_thread()  # Prevents hanging process

    assert not recorder.is_alive(), "Recorder thread did not stop!"
    assert isinstance(audio_data, np.ndarray)
    assert audio_data.shape == (config.CHUNK_SIZE,)

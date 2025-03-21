import pytest
import numpy as np
import multiprocessing as mp
import threading
import time
import torchaudio
from live_translation._transcription._transcriber import Transcriber
from live_translation.config import Config
from live_translation._output import OutputManager


@pytest.fixture
def processed_audio_queue():
    queue = mp.Queue()
    yield queue
    queue.cancel_join_thread()  # Prevents hanging process
    queue.close()


@pytest.fixture
def transcription_queue():
    queue = mp.Queue()
    yield queue
    queue.cancel_join_thread()  # Prevents hanging process
    queue.close()


@pytest.fixture
def stop_event():
    return threading.Event()


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def output_manager(config):
    return OutputManager(config)


@pytest.fixture
def real_speech():
    """Load a real speech sample."""
    waveform, _ = torchaudio.load("tests/audio_samples/sample.wav")
    return waveform[0].numpy().astype(np.float32)


def test_transcriber_pipeline(
    processed_audio_queue,
    transcription_queue,
    stop_event,
    config,
    output_manager,
    real_speech,
):
    """Populate queue, start Transcriber, and check transcription queue."""

    processed_audio_queue.put(real_speech)

    transcriber = Transcriber(
        processed_audio_queue, transcription_queue, stop_event, config, output_manager
    )
    transcriber.start()

    time.sleep(10)

    assert not transcription_queue.empty(), "❌ Transcription queue should contain text"

    transcription = transcription_queue.get()

    stop_event.set()
    transcriber.join(timeout=3)

    transcriber._cleanup()

    if transcriber.is_alive():
        transcriber.terminate()

    assert isinstance(transcription, str) and len(transcription) > 0, (
        "❌ Transcription output is incorrect!"
    )

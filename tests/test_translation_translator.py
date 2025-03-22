import pytest
import multiprocessing as mp
import threading
import time
from live_translation._translation._translator import Translator
from live_translation.config import Config


@pytest.fixture
def transcription_queue():
    queue = mp.Queue()
    yield queue
    queue.cancel_join_thread()
    queue.close()


@pytest.fixture
def output_queue():
    queue = mp.Queue()
    yield queue
    queue.cancel_join_thread()
    queue.close()


@pytest.fixture
def stop_event():
    return threading.Event()


@pytest.fixture
def config():
    return Config(output="print", transcribe_only=False)


@pytest.fixture
def random_text():
    return "Hello, how are you?"


def test_translator_pipeline(
    transcription_queue, output_queue, stop_event, config, random_text
):
    """Test Translator in full pipeline mode with output queue."""

    transcription_queue.put(random_text)

    translator = Translator(transcription_queue, stop_event, config, output_queue)
    translator.start()

    time.sleep(5)

    stop_event.set()
    translator.join(timeout=3)

    if translator.is_alive():
        translator.terminate()

    assert not output_queue.empty(), "Output queue should contain an entry"
    entry = output_queue.get()

    assert isinstance(entry, dict)
    assert "transcription" in entry, "Transcription should be present"
    assert "translation" in entry, "Translation should be present"
    assert len(entry["transcription"].strip()) > 0, "Transcription should not be empty"
    assert len(entry["translation"].strip()) > 0, "Translation should not be empty"

    assert "Hello, how are you?" in entry["transcription"], "Transcription should match"
    assert "Hola, ¿cómo estás?" in entry["translation"], "Translation should match"

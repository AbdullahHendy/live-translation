import pytest
import multiprocessing as mp
import threading
import time
import json
import os
from live_translation._translation._translator import Translator
from live_translation.config import Config
from live_translation._output import OutputManager

TRANSCRIPTS_DIR = "transcripts/"


@pytest.fixture
def transcription_queue():
    queue = mp.Queue()
    yield queue
    queue.cancel_join_thread()
    queue.close()


@pytest.fixture
def stop_event():
    return threading.Event()


@pytest.fixture
def config():
    cfg = Config(output="file")
    return cfg


@pytest.fixture
def output_manager(config):
    return OutputManager(config)


@pytest.fixture
def random_text():
    """Provide a random text input for translation."""
    return "Hello, how are you?"


def get_latest_transcript():
    """Find the latest transcript file in the transcripts directory."""
    files = sorted(
        [f for f in os.listdir(TRANSCRIPTS_DIR) if f.endswith(".json")],
        key=lambda f: os.path.getctime(os.path.join(TRANSCRIPTS_DIR, f)),
    )
    return os.path.join(TRANSCRIPTS_DIR, files[-1]) if files else None


def test_translator_pipeline(
    transcription_queue, stop_event, config, output_manager, random_text
):
    """Populate queue, start Translator, and check transcription JSON file."""

    transcription_queue.put(random_text)

    translator = Translator(transcription_queue, stop_event, config, output_manager)
    translator.start()

    time.sleep(5)

    stop_event.set()
    translator.join(timeout=3)

    translator._cleanup()

    if translator.is_alive():
        translator.terminate()

    transcript_file = get_latest_transcript()
    assert transcript_file, "No transcript file was created"

    with open(transcript_file, "r") as f:
        data = json.load(f)
    assert isinstance(data, list) and len(data) > 0, (
        "Transcript file does not contain valid data"
    )

    data = data[0]

    assert "Hello, how are you?" in data["transcription"], (
        "Transcription missing expected text"
    )
    assert "Hola, ¿cómo estás?" in data["translation"], (
        "Translation missing expected text"
    )

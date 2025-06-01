from unittest import mock
import pytest
import multiprocessing as mp
import time
from live_translation._translation._translator import Translator
from live_translation.server.config import Config


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
    return mp.Event()


@pytest.fixture
def config():
    return Config(transcribe_only=False)


@pytest.fixture
def test_text():
    return "Hello, how are you?"


def test_translator_pipeline(
    transcription_queue, output_queue, stop_event, config, test_text
):
    """Test Translator in full pipeline mode with output queue."""

    transcription_queue.put(test_text)

    translator = Translator(transcription_queue, stop_event, config, output_queue)
    translator.start()

    timeout = 20
    poll_interval = 0.1
    waited = 0
    while output_queue.empty() and waited < timeout:
        time.sleep(poll_interval)
        waited += poll_interval

    assert not output_queue.empty(), "Output queue should contain an entry"

    stop_event.set()
    translator.join(timeout=3)

    if translator.is_alive():
        translator.terminate()

    entry = output_queue.get()

    assert isinstance(entry, dict)
    assert "transcription" in entry, "Transcription should be present"
    assert "translation" in entry, "Translation should be present"
    assert len(entry["transcription"].strip()) > 0, "Transcription should not be empty"
    assert len(entry["translation"].strip()) > 0, "Translation should not be empty"

    assert "Hello, how are you?" in entry["transcription"], "Transcription should match"
    assert "Hola, ¿cómo estás?" in entry["translation"], "Translation should match"


def test_translate_skips_empty_text(config):
    """_translate should return '' for empty/whitespace-only input."""

    translator = Translator(
        transcription_queue=mp.Queue(),
        stop_event=mp.Event(),
        cfg=config,
        output_queue=mp.Queue(),
    )

    result = translator._translate("   ")
    assert result == ""


def test_translator_critical_error(config, capfd):
    """Test critical error during model loading is logged."""

    translator = Translator(
        transcription_queue=mp.Queue(),
        stop_event=mp.Event(),
        cfg=config,
        output_queue=mp.Queue(),
    )

    # Patch the model loading to raise an error
    with (
        mock.patch(
            "transformers.MarianMTModel.from_pretrained",
            side_effect=RuntimeError("load fail"),
        ),
        mock.patch.object(translator, "_cleanup"),
    ):
        translator.run()

    out, _ = capfd.readouterr()
    assert "🚨 Critical Translator Error: load fail" in out

import pytest
import numpy as np
import multiprocessing as mp
import threading
import time
import torchaudio
from live_translation._transcription._transcriber import Transcriber
from live_translation.config import Config


@pytest.fixture
def processed_audio_queue():
    queue = mp.Queue()
    yield queue
    queue.cancel_join_thread()
    queue.close()


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
def real_speech():
    waveform, _ = torchaudio.load("tests/audio_samples/sample.wav")
    return waveform[0].numpy().astype(np.float32)


def test_transcriber_pipeline_output_queue(
    processed_audio_queue,
    output_queue,
    stop_event,
    real_speech,
):
    # Transcriber in transcribe_only mode → sends to output_queue
    config = Config(transcribe_only=True, output="print")

    processed_audio_queue.put(real_speech)

    transcriber = Transcriber(
        processed_audio_queue,
        transcription_queue=mp.Queue(),
        stop_event=stop_event,
        cfg=config,
        output_queue=output_queue,
    )
    transcriber.start()
    time.sleep(10)

    assert not output_queue.empty(), "Output queue should contain an entry"

    entry = output_queue.get()
    stop_event.set()
    transcriber.join(timeout=3)
    if transcriber.is_alive():
        transcriber.terminate()

    assert isinstance(entry, dict)
    assert "transcription" in entry
    assert len(entry["transcription"].strip()) > 0


def test_transcriber_pipeline_transcription_queue(
    processed_audio_queue,
    stop_event,
    transcription_queue,
    real_speech,
):
    # Transcriber in full pipeline mode → sends plain text to transcription_queue
    config = Config(transcribe_only=False, output="file")
    output_queue = mp.Queue()  # still required but unused

    processed_audio_queue.put(real_speech)

    transcriber = Transcriber(
        processed_audio_queue,
        transcription_queue=transcription_queue,
        stop_event=stop_event,
        cfg=config,
        output_queue=output_queue,
    )
    transcriber.start()
    time.sleep(10)

    assert not transcription_queue.empty(), "Transcription queue should contain text"

    transcription = transcription_queue.get()
    stop_event.set()
    transcriber.join(timeout=3)
    if transcriber.is_alive():
        transcriber.terminate()

    assert isinstance(transcription, str)
    assert len(transcription.strip()) > 0

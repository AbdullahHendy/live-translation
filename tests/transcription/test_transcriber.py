from unittest import mock
import pytest
import numpy as np
import multiprocessing as mp
import time
import torchaudio
from live_translation._transcription._transcriber import Transcriber
from live_translation.server.config import Config


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
    return mp.Event()


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
    config = Config(transcribe_only=True)

    processed_audio_queue.put(real_speech)

    transcriber = Transcriber(
        processed_audio_queue,
        transcription_queue=mp.Queue(),
        stop_event=stop_event,
        cfg=config,
        output_queue=output_queue,
    )
    transcriber.start()

    timeout = 25  # Audio file 'sample.wav' is about 17 seconds long
    poll_interval = 0.1
    waited = 0
    # Although it's not strictly necessary to wait for the whole 'processed_audio_queue'
    # to be processed, it helps to make sure we don't miss any edge cases that might
    # occur with longer audio chunks.
    while (
        not processed_audio_queue.empty() or output_queue.empty()
    ) and waited < timeout:
        time.sleep(poll_interval)
        waited += poll_interval

    assert not output_queue.empty(), "Output queue should contain an entry"

    entry = output_queue.get()
    stop_event.set()
    transcriber.join(timeout=3)
    if transcriber.is_alive():
        transcriber.terminate()

    assert isinstance(entry, dict)
    assert "transcription" in entry
    assert (
        " Hello, good morning everyone. I hope everyone's doing good and staying safe."
        " This is a test for the live translation program.  Thank you."
        in entry["transcription"]
    )
    assert len(entry["transcription"].strip()) > 0


def test_transcriber_pipeline_transcription_queue(
    processed_audio_queue,
    stop_event,
    transcription_queue,
    real_speech,
):
    # Transcriber in full pipeline mode → sends plain text to transcription_queue
    config = Config(transcribe_only=False)
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

    timeout = 25  # Audio file 'sample.wav' is about 17 seconds long
    poll_interval = 0.1
    waited = 0
    # Allow for the whole processed audio queue to be processed for better coverage.
    while (
        not processed_audio_queue.empty() or output_queue.empty()
    ) and waited < timeout:
        time.sleep(poll_interval)
        waited += poll_interval
    assert not transcription_queue.empty(), "Transcription queue should contain text"
    assert output_queue.empty(), "Output queue should be empty"
    transcription = transcription_queue.get()
    stop_event.set()
    transcriber.join(timeout=3)
    if transcriber.is_alive():
        transcriber.terminate()

    assert isinstance(transcription, str)
    assert len(transcription.strip()) > 0


def test_transcriber_skip_empty_transcription():
    """Test that silent audio does not produce any output."""

    # One second of silent audio (16kHz, float32)
    # Fun fact: longer silence than 1 second will most likely still cause whisper to
    # produce a transcription of random words. This makes sense since default whisper
    # is not a silent detector without enabling its internal VAD, which is not useful
    # for our use case as we used our own VAD in the audio processor.
    silent_audio = np.zeros(16000, dtype=np.float32)
    print(f"Silent audio shape: {silent_audio.shape}")
    processed_audio_queue = mp.Queue()
    output_queue = mp.Queue()
    stop_event = mp.Event()

    processed_audio_queue.put(silent_audio)

    cfg = Config(transcribe_only=True)
    transcriber = Transcriber(
        processed_audio_queue=processed_audio_queue,
        transcription_queue=mp.Queue(),
        stop_event=stop_event,
        cfg=cfg,
        output_queue=output_queue,
    )

    transcriber.start()

    while not processed_audio_queue.empty():
        time.sleep(0.1)

    stop_event.set()
    transcriber.join(timeout=5)
    if transcriber.is_alive():
        transcriber.terminate()

    assert output_queue.empty(), "Silent audio should not produce any transcription"


def test_transcriber_critical_error(capfd):
    """Test outer critical error is caught and logged."""

    transcriber = Transcriber(
        processed_audio_queue=mock.Mock(),
        transcription_queue=mock.Mock(),
        stop_event=mock.Mock(),
        cfg=Config(),
        output_queue=mock.Mock(),
    )

    # Inject failure right at the beginning of run() (WhisperModel initialization)
    with (
        mock.patch(  # patch the WhisperModel initialization to raise an error
            "live_translation._transcription._transcriber.WhisperModel",
            side_effect=RuntimeError("load fail"),
        ),
        mock.patch.object(transcriber, "_cleanup"),
    ):
        transcriber.run()

    out, _ = capfd.readouterr()
    assert "🚨 Critical Transcriber Error: load fail" in out


def test_transcriber_cleanup_exception(capfd):
    """Test _cleanup handles exceptions during queue close."""
    transcriber = Transcriber(
        processed_audio_queue=mock.Mock(),
        transcription_queue=mock.Mock(),
        stop_event=mock.Mock(),
        cfg=Config(),
        output_queue=mock.Mock(),
    )

    # Cause an exception when closing the transcription queue
    transcriber._transcription_queue.close.side_effect = RuntimeError("fail on close")

    # Should not raise
    transcriber._cleanup()

    out, _ = capfd.readouterr()
    assert "🚨 Transcriber Cleanup Error: fail on close" in out

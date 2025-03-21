# audio/_recorder.py

import multiprocessing as mp
import threading
import numpy as np
import pyaudio
from .. import config


class AudioRecorder(threading.Thread):
    """
    Captures raw audio from the input and sends it to a queue for processing.
    """

    def __init__(
        self, audio_queue: mp.Queue, stop_event: threading.Event, cfg: config.Config
    ):
        """Initialize the AudioRecorder."""

        super().__init__()
        self._audio_queue = audio_queue
        self._stop_event = stop_event
        self._cfg = cfg
        # Initialize PyAudio
        self._pyaudio_instance = pyaudio.PyAudio()
        self._stream = self._pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=self._cfg.CHANNELS,
            rate=self._cfg.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self._cfg.CHUNK_SIZE,
        )

    def run(self):
        """Continuously capture audio and push to the queue."""
        print("🎤 Recorder: Listening...")

        try:
            while not self._stop_event.is_set():
                try:
                    data = self._stream.read(
                        self._cfg.CHUNK_SIZE, exception_on_overflow=False
                    )
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    self._audio_queue.put(audio_data)
                except Exception as e:
                    print(f"🚨 Recorder Error: {e}")
                    continue
        finally:
            self._cleanup()
            print("🎤 Recorder: Stopped.")

    def _cleanup(self):
        """Stop audio stream and terminate PyAudio."""
        try:
            if self._stream.is_active():
                self._stream.stop_stream()
            self._stream.close()
            self._pyaudio_instance.terminate()
            self._audio_queue.close()
        except Exception as e:
            print(f"🚨 Recorder Cleanup Error: {e}")

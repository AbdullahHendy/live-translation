# audio/recorder.py

import multiprocessing as mp
import threading
import numpy as np
import pyaudio
import config

class AudioRecorder(threading.Thread):
    """
    Captures raw audio from the input and sends it to a queue for processing.
    """
    def __init__(self, audio_queue: mp.Queue, 
                 stop_event: threading.Event, 
                 cfg: config.Config
                ):
        """Initialize the AudioRecorder."""

        super().__init__()
        self.audio_queue = audio_queue
        self.stop_event = stop_event
        self.cfg = cfg

        # Initialize PyAudio
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=self.cfg.CHANNELS,
            rate=self.cfg.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.cfg.CHUNK_SIZE,
        )

    def run(self):
        """Continuously capture audio and push to the queue."""
        print("🎤 Recorder: Listening...")

        try:
            while not self.stop_event.is_set():
                try:
                    data = self.stream.read(self.cfg.CHUNK_SIZE, 
                                            exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    self.audio_queue.put(audio_data)
                except Exception as e:
                    print(f"🚨 Recorder Error: {e}")
                    continue
        finally:
            self._cleanup()
            print("🎤 Recorder: Stopped.")

    def _cleanup(self):
        """Stop audio stream and terminate PyAudio."""
        try:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
            self.pyaudio_instance.terminate()
            self.audio_queue.close()
        except Exception as e:
            print(f"🚨 Recorder Cleanup Error: {e}")

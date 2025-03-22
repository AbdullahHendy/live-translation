# transcription/_transcriber.py

from datetime import datetime, timezone
import queue
import multiprocessing as mp
import torch
import threading
import numpy as np
from faster_whisper import WhisperModel
from .. import config


class Transcriber(mp.Process):
    """
    Transcriber retrieves audio segments from an audio queue,
    transcribes them using a Whisper model, and pushes the resulting text into
    a transcription queue.
    """

    def __init__(
        self,
        processed_audio_queue: mp.Queue,
        transcription_queue: mp.Queue,
        stop_event: threading.Event,
        cfg: config.Config,
        output_queue: mp.Queue,
    ):
        """Initialize the Transcriber."""

        super().__init__()
        self._audio_queue = processed_audio_queue
        self._transcription_queue = transcription_queue
        self._stop_event = stop_event
        self._cfg = cfg
        self._output_queue = output_queue

    def run(self):
        """Load the Whisper model and transcribe audio segments."""

        print("🔄 Transcriber: Loading Whisper model...")
        self.whisper_model = WhisperModel(
            self._cfg.WHISPER_MODEL, compute_type="float32", device=self._cfg.DEVICE
        )
        print("📝 Transcriber: Ready to transcribe audio...")
        self._stop_event = self._stop_event
        try:
            while not (self._stop_event.is_set() and self._audio_queue.empty()):
                # Get audio segment from the queue
                try:
                    audio_segment = self._audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                try:
                    # Normalize and transcribe the audio segment
                    audio_segment = audio_segment.astype(np.float32)
                    with torch.inference_mode():
                        segments, _ = self.whisper_model.transcribe(
                            audio_segment, language=self._cfg.SRC_LANG
                        )

                    transcription = " ".join(seg.text for seg in segments)
                    if transcription.strip():
                        if self._cfg.TRANSCRIBE_ONLY:
                            entry = {
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "transcription": transcription,
                                "translation": "",
                            }
                            self._output_queue.put(entry)
                        else:
                            self._transcription_queue.put(transcription)
                except Exception as e:
                    print(f"🚨 Transcriber Error: {e}")
        except Exception as e:
            print(f"❌ Critical Transcriber Error: {e}")
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()
            print("📝 Transcriber: Stopped.")

    def _cleanup(self):
        """Clean up the Whisper model."""
        try:
            self._transcription_queue.close()
        except Exception as e:
            print(f"🚨 Transcriber Cleanup Error: {e}")

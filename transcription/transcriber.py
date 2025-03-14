# transcription/transcriber.py

import queue
import multiprocessing as mp
import torch
import threading
import numpy as np
from faster_whisper import WhisperModel
import config
from output_manager import OutputManager


class Transcriber(mp.Process):
    """
    Transcriber retrieves audio segments from an audio queue, 
    transcribes them using a Whisper model, and pushes the resulting text into 
    a transcription queue.
    """
    def __init__(self, processed_audio_queue: mp.Queue, 
                 transcription_queue: mp.Queue, 
                 stop_event: threading.Event, 
                 cfg: config.Config, 
                 output_manager: OutputManager
                ):
        """Initialize the Transcriber. """

        super().__init__()
        self.audio_queue = processed_audio_queue
        self.transcription_queue = transcription_queue
        self.stop_event = stop_event
        self.cfg = cfg
        self.output_manager = output_manager
    
    def run(self):
        """Load the Whisper model and transcribe audio segments."""

        print("🔄 Transcriber: Loading Whisper model...")
        self.whisper_model = WhisperModel(self.cfg.WHISPER_MODEL, 
                                          compute_type="float32",
                                          device=self.cfg.DEVICE)
        print("📝 Transcriber: Ready to transcribe audio...")
        self.stop_event = self.stop_event
        try:
            while not (self.stop_event.is_set() and self.audio_queue.empty()):
                # Get audio segment from the queue
                try:
                    audio_segment = self.audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                try:
                    # Normalize and transcribe the audio segment
                    audio_segment = audio_segment.astype(np.float32)
                    with torch.inference_mode():
                        segments, _ = self.whisper_model.transcribe(
                            audio_segment, language=self.cfg.SRC_LANG
                        )
                    
                    transcription = " ".join(seg.text for seg in segments)
                    if transcription.strip():
                        if self.cfg.TRANSCRIBE_ONLY:
                            self.output_manager.write(transcription)
                        else:
                            self.transcription_queue.put(transcription)
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
            self.transcription_queue.close()
        except Exception as e:
            print(f"🚨 Transcriber Cleanup Error: {e}")
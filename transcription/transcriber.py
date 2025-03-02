# transcription/transcriber.py

import queue
import multiprocessing as mp
import threading
import numpy as np
from faster_whisper import WhisperModel
from config import WHISPER_MODEL, SRC_LANG, DEVICE

class Transcriber(mp.Process):
    """
    Transcriber retrieves audio segments from an audio queue, 
    transcribes them using a Whisper model, and pushes the resulting text into 
    a transcription queue.
    """
    def __init__(self, audio_queue: mp.Queue, 
                 transcription_queue: mp.Queue, 
                 stop_event: threading.Event):
        super().__init__()
        self.audio_queue = audio_queue
        self.transcription_queue = transcription_queue
        self.stop_event = stop_event
    
    def run(self):
        print("🔄 Transcriber: Loading Whisper model...")
        self.whisper_model = WhisperModel(WHISPER_MODEL, device=DEVICE)
        print("📝 Transcriber: Ready to transcribe audio...")

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
                    segments, _ = self.whisper_model.transcribe(
                        audio_segment, language=SRC_LANG
                    )
                    
                    transcription = " ".join(seg.text for seg in segments)
                    if transcription.strip():
                        print(f"📝 Transcriber: {transcription}")
                        self.transcription_queue.put(transcription)
                except Exception as e:
                    print(f"🚨 Transcriber Error: {e}")
        except Exception as e:
            print(f"❌ Critical Transcriber Error: {e}")
        finally:
            print("📝 Transcriber: Stopped.")

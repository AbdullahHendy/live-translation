# transcription/transcriber.py

import time
import queue
import threading
import numpy as np
from faster_whisper import WhisperModel
from config import WHISPER_MODEL, SRC_LANG, DEVICE

class Transcriber(threading.Thread):
    """
    Transcriber retrieves audio segments from an audio queue, 
    transcribes them using a Whisper model, and pushes the resulting text into 
    a transcription queue.
    """
    def __init__(self, audio_queue: queue.Queue, 
                 transcription_queue: queue.Queue, 
                 stop_event: threading.Event):
        super().__init__()
        self.audio_queue = audio_queue
        self.transcription_queue = transcription_queue
        self.stop_event = stop_event
        print("🔄 Transcriber: Loading Whisper model...")
        self.whisper_model = WhisperModel(WHISPER_MODEL, device=DEVICE)
    
    def run(self):
        print("📝 Transcriber: Ready to transcribe audio...")
        while not (self.stop_event.is_set() and self.audio_queue.empty()):
            try:
                # Wait for audio to become available
                # TODO: Reconsider the timeout value
                audio_segment = self.audio_queue.get(timeout=1)
            except queue.Empty:
                continue
            try:
                # Ensure audio is in the correct format (normalized float32)
                audio_segment = audio_segment.astype(np.float32)
                segments, _ = self.whisper_model.transcribe(
                    audio_segment, language=SRC_LANG
                )
                transcription = " ".join(segment.text for segment in segments)
                if transcription.strip():
                    print(f"📝 Transcriber: {transcription}")
                    self.transcription_queue.put(transcription)
            except Exception as e:
                print(f"Transcriber Error: {e}")

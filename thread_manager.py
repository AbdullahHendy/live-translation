# thread_manager.py

import time
import queue
import threading
from audio.recorder import AudioRecorder
from transcription.transcriber import Transcriber
from translation.translator import Translator

class ThreadManager:
    def __init__(self):
        # Queues for inter-thread communication
        self.audio_queue = queue.Queue()
        self.transcription_queue = queue.Queue()
        
        # Event to signal threads to stop
        self.stop_event = threading.Event()

        # Create component instances
        self.recorder = AudioRecorder(self.audio_queue, self.stop_event)
        self.transcriber = Transcriber(self.audio_queue, self.transcription_queue, self.stop_event)
        self.translator = Translator(self.transcription_queue, self.stop_event)

    def start_threads(self):
        """Start all threads"""
        self.recorder.start()
        self.transcriber.start()
        self.translator.start()

    def stop_threads(self):
        """Stop all threads gracefully"""
        print("\n🛑 Stopping all threads...")
        self.stop_event.set()
        # Ensure all threads shut down cleanly
        self.recorder.join()
        self.transcriber.join()
        self.translator.join()
        print("✅ All threads stopped.")
        
    def run(self):
        """Run the thread manager"""
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop_threads()

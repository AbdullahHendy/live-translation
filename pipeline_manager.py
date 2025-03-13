# pipeline_manager.py

import os
import multiprocessing as mp
import signal
import time
from audio.recorder import AudioRecorder
from audio.processor import AudioProcessor
from transcription.transcriber import Transcriber
from translation.translator import Translator
from output_manager import OutputManager
import config


class PipelineManager:
    def __init__(self, config: config.Config):
        """
        Initialize config, queues, stop event, thread, and processes.
        """
        self.config = config

        # Multiprocessing context and manager
        ctx = mp.get_context()
        self.manager = ctx.Manager()
        self.stop_event = self.manager.Event()
        self.parent_pid = os.getpid()
        
        # Queues for inter-process communication
        self.raw_audio_queue = mp.Queue()
        self.processed_audio_queue = mp.Queue()
        self.transcription_queue = mp.Queue()

        # Create OutputManager
        self.output_manager = OutputManager(
            self.config
            )

        # Thread
        self.audio_recorder = AudioRecorder(
            self.raw_audio_queue, 
            self.stop_event,
            self.config
        )
        # Processes
        self.audio_processor = AudioProcessor(
            self.raw_audio_queue, 
            self.processed_audio_queue, 
            self.stop_event,
            self.config
        )

        self.transcriber = Transcriber(
            self.processed_audio_queue, 
            self.transcription_queue, 
            self.stop_event,
            self.config, 
            self.output_manager
        )

        self.translator = Translator(
            self.transcription_queue, 
            self.stop_event,
            self.config,
            self.output_manager
        )

        # List of pipeline components
        self.threads = [self.audio_recorder]
        self.processes = [self.audio_processor, 
                          self.transcriber, 
                          self.translator]

    def signal_handler(self, sig, frame):
        """Handle Ctrl+C: Parent process only should handles it."""
        if os.getpid() != self.parent_pid:
            return  # Ignore SIGINT in child processes

        print("\n🛑 Stopping the pipeline...")
        self.stop_event.set()

    def start_pipeline(self):
        """Start the audio thread and processes."""
        print("🚀 Starting the pipeline...")

        # Register all components as daemon processes
        for thread in self.threads:
            thread.daemon = True
        
        for process in self.processes:
            process.daemon = True
        
        # Start all components
        for thread in self.threads:
            thread.start()
        
        for process in self.processes:
            process.start()

    def stop_pipeline(self):
        """Gracefully stop all components."""

        # Allow all components to finish processing
        for thread in self.threads:
            thread.join(timeout=5)

        for process in self.processes:
            process.join(timeout=5)

        # Forcefully terminate any stuck processes
        for process in self.processes:
            if process.is_alive():
                print(
                    f"🚨 {process.__class__.__name__} did not stop gracefully."
                    "Terminating."
                )                
                process.terminate()
        
        self.output_manager.close()

        print("✅ All processes stopped.")

    def run(self):
        """Run the pipeline manager and handle shutdown signals."""
        # Register signal handler
        signal.signal(signal.SIGINT, self.signal_handler)

        try:
            self.start_pipeline()

            while not self.stop_event.is_set():
                time.sleep(0.1)
        finally:
            self.stop_pipeline()

# audio/recorder.py

import time
# import queue
import multiprocessing as mp
import threading
import numpy as np
import pyaudio
from audio.vad import VoiceActivityDetector
import config


class AudioRecorder(threading.Thread):
    """
    AudioRecorder captures audio from the microphone, applies VAD, 
    and pushes audio segments into a provided queue for further processing.
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
        self.vad = VoiceActivityDetector(self.cfg.VAD_AGGRESSIVENESS)
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=self.cfg.CHANNELS,
            rate=self.cfg.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.cfg.CHUNK_SIZE,
        )
        
    def run(self):
        """Capture audio, apply VAD, and push audio segments into the queue."""

        silence_count = 0
        audio_buffer = []
        print("🎤 Recorder: Listening for speech...")
        
        try:
            while not self.stop_event.is_set():
                try:
                    data = self.stream.read(
                        self.cfg.CHUNK_SIZE, exception_on_overflow=False
                    )
                except Exception as e:
                    print(f"🚨 Recorder Error: {e}")
                    continue

                audio_data = np.frombuffer(data, dtype=np.int16)
                audio_data_f32 = self.int2float(audio_data)
                
                # Check if current audio chunk contains speech
                if self.vad.is_speech(audio_data_f32, self.cfg.SAMPLE_RATE):
                    # Reset silence counter if there's speech
                    silence_count = 0  
                    # Append audio data to the buffer
                    audio_buffer.append(audio_data_f32)  
                else:
                    silence_count += 1
                    # Once there is enough consecutive non-speech frames, 
                    # enqueue the audio in the buffer
                    if (silence_count >= self.cfg.SILENCE_THRESHOLD and 
                        audio_buffer):
                        # Concatenate and normalize the audio buffer
                        audio_segment = np.concatenate(audio_buffer)

                        self.audio_queue.put(audio_segment)
                        # Reset audio buffer and silence counter
                        audio_buffer = []
                        silence_count = 0
                
                time.sleep(0.01)

        except Exception as e:
            print(f"❌ Critical Recorder Error: {e}")
        finally:
            # Clean up in case of an exception or stop event
            self._cleanup()
            print("🎤 Recorder: Stopped.")

    def _cleanup(self):
        """Stop the audio stream and terminate the PyAudio instance."""
        try:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
            self.pyaudio_instance.terminate()
        except Exception as e:
            print(f"🚨 Recorder Cleanup Error: {e}")

    @staticmethod
    def int2float(sound: np.ndarray):
        """Convert int16 audio to float32 for Silero VAD."""
        sound = sound.astype('float32')
        max_val = np.abs(sound).max()
        # if there is any audio in the segment, normalize it
        if max_val > 0:
            sound *= 1 / np.iinfo(np.int16).max
        return sound
    
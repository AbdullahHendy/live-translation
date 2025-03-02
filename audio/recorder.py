# audio/recorder.py

import time
# import queue
import multiprocessing as mp
import threading
import numpy as np
import pyaudio
import webrtcvad
from config import (CHUNK_SIZE, SAMPLE_RATE, CHANNELS, SILENCE_THRESHOLD, 
                    VAD_AGGRESSIVENESS)

class AudioRecorder(threading.Thread):
    """
    AudioRecorder captures audio from the microphone, applies VAD, 
    and pushes audio segments into a provided queue for further processing.
    """
    def __init__(self, audio_queue: mp.Queue, stop_event: threading.Event):
        super().__init__()
        self.audio_queue = audio_queue
        self.stop_event = stop_event
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = self.pyaudio_instance.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )
        
    def run(self):
        silence_count = 0
        audio_buffer = []
        print("🎤 Recorder: Listening for speech...")
        
        try:
            while not self.stop_event.is_set():
                try:
                    data = self.stream.read(
                        CHUNK_SIZE, exception_on_overflow=False
                    )
                except Exception as e:
                    print(f"🚨 Recorder Error: {e}")
                    continue

                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Check if current audio chunk contains speech
                if self.vad.is_speech(audio_data.tobytes(), SAMPLE_RATE):
                    # Reset silence counter if there's speech
                    silence_count = 0  
                    # Append audio data to the buffer
                    audio_buffer.append(audio_data)  
                else:
                    silence_count += 1
                    # Once there is enough consecutive non-speech frames, 
                    # enqueue the audio in the buffer
                    if silence_count >= SILENCE_THRESHOLD and audio_buffer:
                        # Concatenate and normalize the audio buffer
                        audio_segment = (
                            np.concatenate(audio_buffer).astype(np.float32) /
                            np.iinfo(np.int16).max
                        )

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
        try:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
            self.pyaudio_instance.terminate()
        except Exception as e:
            print(f"🚨 Recorder Cleanup Error: {e}")

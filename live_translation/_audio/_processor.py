# audio/_processor.py

import multiprocessing as mp
import queue
import threading
import numpy as np
import time
from ._vad import VoiceActivityDetector
from .. import config


class AudioProcessor(mp.Process):
    """
    Processes raw audio from the queue, applies _VAD, buffers, and
    sends cleaned audio to another queue for transcription.
    """

    def __init__(
        self,
        audio_queue: mp.Queue,
        processed_queue: mp.Queue,
        stop_event: threading.Event,
        cfg: config.Config,
    ):
        super().__init__()
        self._audio_queue = audio_queue
        self._processed_queue = processed_queue
        self._stop_event = stop_event
        self._cfg = cfg
        self._vad = None
        self._audio_buffer = []

    def run(self):
        """
        Continuously process raw audio from the queue.

        ALGORITHM:
        1. Receive raw audio chunks from sent by `AudioRecorder`.
        2. Apply VAD to check if speech is present.
        3. If speech is detected:
            - Reset `silence_count` (since we are in active speech).
            - Append the new chunk to `audio_buffer` (context accumulation).
            - Check if we have at least `ENQUEUE_THRESHOLD` seconds of
            new speech:
                - If yes, concatenate the buffer and send it to
                `processed_queue` for transcription.
                - Update `last_sent_len` to track how much has been sent.
            - If the total `audio_buffer` duration exceeds
            `MAX_BUFFER_DURATION`:
                - Trim the buffer by removing `TRIM_FACTOR`.
                - Update `audio_buffer_start_len` to track the new
                starting position.
                - Adjust `last_sent_len` to ensure proper tracking after
                trimming.
        4. If silence is detected:
            - Increment `silence_count` to track consecutive silent chunks.
            - If `silence_count` reaches `SOFT_SILENCE_THRESHOLD`:
                - If there is any speech in the buffer (new speech that hasn't exceeded
                ENQUEUE_THRESHOLD yet to get enqueued normally):
                    - Concatenate the buffer and send it to `processed_queue`.
                    - Update `last_sent_len` to track how much has been sent.
            - If silence persists beyond `SILENCE_THRESHOLD`:
                - Reset the buffer (since speech has clearly stopped).
                - Reset `last_sent_len` and `silence_count`.
        """
        self._vad = VoiceActivityDetector(self._cfg.VAD_AGGRESSIVENESS)
        silence_count = 0  # Track consecutive silence
        last_sent_len = 0  # Track last enqueue position
        # Track the buffer start length to calculate buffer duration from
        _audio_buffer_start_len = 0

        print("🔄 AudioProcessor: Ready to process audio...")

        try:
            while not self._stop_event.is_set():
                try:
                    audio_data = self._audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue  # Skip if queue is empty

                audio_data_f32 = self._int2float(audio_data)

                # Run _VAD
                has_speech = self._vad.is_speech(audio_data_f32, self._cfg.SAMPLE_RATE)

                if has_speech:
                    silence_count = 0

                    # Append an audio chunk to the buffer
                    self._audio_buffer.append(audio_data_f32)

                    # Enqueue if Xs of new audio is available
                    new_audio = self._audio_buffer[last_sent_len:]
                    new_duration = self._buffer_duration_s(len(new_audio), 0)
                    # If we have enough new audio, enqueue it
                    if new_duration >= self._cfg.ENQUEUE_THRESHOLD:
                        audio_segment = np.concatenate(self._audio_buffer)
                        self._processed_queue.put(audio_segment)
                        last_sent_len = len(self._audio_buffer)

                    # Trim buffer if it exceeds max duration
                    total_duration = self._buffer_duration_s(
                        len(self._audio_buffer), _audio_buffer_start_len
                    )
                    if total_duration > self._cfg.MAX_BUFFER_DURATION:
                        trim_size = int(len(self._audio_buffer) * self._cfg.TRIM_FACTOR)
                        self._audio_buffer = self._audio_buffer[trim_size:]
                        _audio_buffer_start_len = len(self._audio_buffer)
                        last_sent_len = max(0, last_sent_len - trim_size)

                else:
                    silence_count += 1

                    # Enqueue short speech segments or end of speech
                    if (
                        silence_count == self._cfg.SOFT_SILENCE_THRESHOLD
                        and self._audio_buffer
                    ):
                        audio_segment = np.concatenate(self._audio_buffer)
                        self._processed_queue.put(audio_segment)
                        last_sent_len = len(self._audio_buffer)

                    # Reset buffer on long silence
                    if silence_count >= self._cfg.SILENCE_THRESHOLD:
                        self._audio_buffer = []
                        last_sent_len = 0
                        silence_count = 0

                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()
            print("🔄 AudioProcessor: Stopped.")

    def _cleanup(self):
        """Clean up the processor."""
        try:
            self._processed_queue.close()
        except Exception as e:
            print(f"🚨 AudioProcessor Cleanup Error: {e}")

    def _buffer_duration_s(self, curr_length, start_length):
        """Calculate buffer duration in seconds since buffer's start_length."""
        return (
            (curr_length - start_length) * self._cfg.CHUNK_SIZE / self._cfg.SAMPLE_RATE
        )

    @staticmethod
    def _int2float(sound):
        """Convert int16 audio to float32 for _VAD."""
        sound = sound.astype("float32")
        max_val = np.abs(sound).max()
        if max_val > 0:
            sound *= 1 / np.iinfo(np.int16).max
        return sound

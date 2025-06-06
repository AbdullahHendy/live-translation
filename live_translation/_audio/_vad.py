# audio/_vad.py

import torch
import numpy as np
from ..server.config import Config


class VoiceActivityDetector:
    """
    Wrapper for Silero VAD model.
    """

    def __init__(self, cfg: Config):
        """
        Initialize Silero VAD model.
        Silero VAD only supports:
        256 chunks at 8000 sample rate or 512 chunks for 16000

        NOTE: Model is intentionally only loaded on CPU since model inference is still
        very fast on CPU and it might not be a good idea to move audio for to GPU for
        inference on very short audio segments.

        See:
        https://github.com/snakers4/silero-vad#live-demonstration
        """
        self._cfg = cfg
        self._model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-vad", model="silero_vad", trust_repo=True
        )

        self._aggressiveness = self._cfg.VAD_AGGRESSIVENESS / 10

    def is_speech(self, audio: np.ndarray):
        """
        Run VAD on an audio segment and determine if it contains speech.
        """
        # validate audio segment type float32
        if audio.dtype != np.float32:
            raise ValueError("🚨 Audio segment must be of type float32")

        chunks = self._slice_audio(audio)

        with torch.inference_mode():
            for chunk in chunks:
                tensor_chunk = torch.tensor(chunk, dtype=torch.float32)
                conf = self._model(tensor_chunk, self._cfg.SAMPLE_RATE).item()
                # If any chunk has a confidence above the threshold,
                # consider the whole audio as speech
                if conf > self._aggressiveness:
                    return True

        return False

    def _slice_audio(self, audio: np.ndarray, vad_frame_size: int = 512):
        """
        Break audio into valid chunks for VAD processing due to Sileros restrictions.
        This is 512 for 16kHz or 256 for 8kHz.
        """
        if len(audio) > vad_frame_size:
            # Non-overlapping chunks of vad_frame_size.
            # Could make overlapping chunks (smaller stride) in the expense of
            # more model inference calls.
            stride = vad_frame_size
            chunks = [
                audio[i : i + vad_frame_size]
                for i in range(0, len(audio) - vad_frame_size + 1, stride)
            ]
            # If the last chunk is not a full stride, add one stride from the tail
            if len(audio) % vad_frame_size != 0:
                tail = audio[-vad_frame_size:]
                chunks.append(tail)
            return chunks
        elif len(audio) == vad_frame_size:
            return [audio]
        # Case when audio is shorter than vad_frame_size should be avoided
        else:
            # Pad the audio to vad_frame_size
            # TODO: consider using a more sophisticated padding strategy
            return [np.pad(audio, (0, vad_frame_size - len(audio)), mode="constant")]

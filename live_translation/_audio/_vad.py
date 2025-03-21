# audio/_vad.py

import torch
import numpy as np


class VoiceActivityDetector:
    """
    Wrapper for Silero VAD model.
    """

    def __init__(self, aggressiveness: float):
        """
        Initialize Silero VAD model.

        aggressiveness: float
            The aggressiveness of the VAD model. The value is in [0, 9]
        """
        self._model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-vad", model="silero_vad"
        )
        self._aggressiveness = aggressiveness / 10

    def is_speech(self, audio: np.ndarray, sample_rate: int):
        """
        Run VAD on an audio segment and determine if it contains speech.
        """
        # validate audio segment type float32
        if audio.dtype != np.float32:
            raise ValueError("🚨 Audio segment must be of type float32")

        confidence = self._model(torch.from_numpy(audio), sample_rate).item()
        return confidence > self._aggressiveness

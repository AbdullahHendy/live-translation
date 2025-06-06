# _audio/_codec.py

import opuslib
from ..server.config import Config


class OpusCodec:
    """
    Codec for encoding and decoding audio using Opus.

    This class provides methods to encode raw audio data into Opus format
    and decode Opus data back into raw audio.
    """

    def __init__(self, cfg: Config):
        self._cfg = cfg
        self._encoder = opuslib.Encoder(
            self._cfg.SAMPLE_RATE, self._cfg.CHANNELS, opuslib.APPLICATION_VOIP
        )
        self._decoder = opuslib.Decoder(self._cfg.SAMPLE_RATE, self._cfg.CHANNELS)

    def encode(self, pcm_data: bytes) -> bytes:
        """
        Encode raw audio data into Opus format.
        Encode must be called with exactly one frame of pcm_data of length
        (2.5, 5, 10, 20, 40 or 60 ms)
        See: https://opus-codec.org/docs/opus_api-1.5/group__opus__encoder.html
        """
        return self._encoder.encode(pcm_data, self._cfg.CHUNK_SIZE)

    def decode(self, opus_data: bytes) -> bytes:
        """Decode Opus data back into raw audio format."""
        return self._decoder.decode(opus_data, self._cfg.CHUNK_SIZE)

# client/config.py


class Config:
    """
    Configuration for the Live Translation Client.

    This class provides explicit configuration settings with default values.

    Args:
        server_uri (str): WebSocket URI of the server (e.g., "ws://localhost:8765")

    """

    def __init__(self, server_uri: str, codec: str = "opus"):
        # Required
        self.SERVER_URI = server_uri

        # Optional
        self.CODEC = codec

        # Immutable audio settings (must match server)
        self._CHUNK_SIZE = 640  # 40 ms of audio at 16 kHz
        self._SAMPLE_RATE = 16000  # Hz
        self._CHANNELS = 1  # Mono

        self._validate()

    def _validate(self):
        if not self.SERVER_URI:
            raise ValueError(
                "🚨 'server_uri' cannot be empty. Use --server to specify it. "
            )

        if not (
            self.SERVER_URI.startswith("ws://") or self.SERVER_URI.startswith("wss://")
        ):
            raise ValueError("🚨 'server_uri' must start with 'ws://' or 'wss://'")

        if self.CODEC not in ["pcm", "opus"]:
            raise ValueError("🚨 'codec' must be either 'pcm' or 'opus'. ")

    @property
    def CHUNK_SIZE(self):
        return self._CHUNK_SIZE

    @property
    def SAMPLE_RATE(self):
        return self._SAMPLE_RATE

    @property
    def CHANNELS(self):
        return self._CHANNELS

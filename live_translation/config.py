# config.py

import torch
import huggingface_hub as hf_hub
import huggingface_hub.errors as hf_errors


class Config:
    """
    Configuration class for the application.

    This class provides explicit configuration settings with default values.

    Args:
        device (str): Device for processing ('cpu', 'cuda'). Default is 'cpu'.

        whisper_model (str): Whisper model size ('tiny', 'base', 'small',
            'medium', 'large', 'large-v2'). Default is 'base'.

        trans_model (str): Translation model ('Helsinki-NLP/opus-mt',
            'Helsinki-NLP/opus-mt-tc-big'). NOTE: Don't include source and
            target languages here. Default is 'Helsinki-NLP/opus-mt'.

        src_lang (str): Source/Input language for transcription (e.g., 'en',
            'fr'). Default is 'en'.

        tgt_lang (str): Target language for translation (e.g., 'es', 'de').
            Default is 'es'.

        output (str): Output method ('print', 'file', 'websocket').
            - 'print': Prints transcriptions and translations to stdout.
            - 'file': Saves structured JSON data in
            transcripts/transcriptions.json.
            - 'websocket': Sends structured JSON data over WebSocket.
            JSON format for 'file' and 'websocket':
            {
                "timestamp": "2025-03-06T12:34:56.789Z",
                "transcription": "Hello world",
                "translation": "Hola mundo"
            }
            Default is 'print'.

        ws_port (int, optional): WebSocket port for sending transcriptions.
            Required if `output="websocket"`.

        silence_threshold (int): Number of consecutive 32ms silent chunks to
            detect SILENCE. SILENCE clears the audio buffer for
            transcription/translation. Default is 65 (~ 2s).

        vad_aggressiveness (int): Voice Activity Detection (VAD) aggressiveness
            level (0-9). Higher values mean VAD has to be more confident to
            detect speech vs silence. Default is 8.

        max_buffer_duration (int): Max audio buffer duration in seconds before
            trimming it. Default is 7 seconds.

        transcribe_only (bool): Whether to only transcribe without translation.
            If set, no translations are performed.
    """

    def __init__(
        self,
        device: str = "cpu",
        whisper_model: str = "base",
        trans_model: str = "Helsinki-NLP/opus-mt",
        src_lang: str = "en",
        tgt_lang: str = "es",
        output: str = "print",
        ws_port: int = None,
        silence_threshold: int = 65,
        vad_aggressiveness: int = 8,
        max_buffer_duration: int = 7,
        transcribe_only: bool = False,
    ):
        """
        Initialize the configuration.
        """

        # Immutable Settings
        # Audio Settings, not all are modifiable for now
        self._CHUNK_SIZE = 512  # 32 ms of audio at 16 kHz
        self._SAMPLE_RATE = 16000  # 16 kHz
        self._CHANNELS = 1  # Mono
        # Audio Processing Settings, not modifiable for now
        # Audio lentgh in seconds to trigger ENQUEUE that is
        # (send for transcription/translation)
        self._ENQUEUE_THRESHOLD = 1  # seconds
        # Trim audio buffer by this percentage when it
        # exceeds MAX_BUFFER_DURATION
        self._TRIM_FACTOR = 0.75
        # Soft silence threshold to detect the end of short speech that might
        # not have exceeded ENQUEUE_THRESHOLD. For example, the end of speech
        # or a short speech segment like "yes" or "no".
        # 16 * 32ms ~ 0.5s
        self._SOFT_SILENCE_THRESHOLD = 16

        # Mutable Settings
        self.DEVICE = device
        self.WHISPER_MODEL = whisper_model
        self.TRANS_MODEL = trans_model
        self.SRC_LANG = src_lang
        self.TGT_LANG = tgt_lang
        self.OUTPUT = output
        self.WS_PORT = ws_port
        self.SILENCE_THRESHOLD = silence_threshold
        self.VAD_AGGRESSIVENESS = vad_aggressiveness
        self.MAX_BUFFER_DURATION = max_buffer_duration
        self.TRANSCRIBE_ONLY = transcribe_only

        # Validate
        self._validate()

    def _validate(self):
        """Validate arguments before applying them."""

        # Validate OpusMT translation model and language pair
        model_name = f"{self.TRANS_MODEL}-{self.SRC_LANG}-{self.TGT_LANG}"
        try:
            hf_hub.model_info(model_name)  # Check if the model exists
        except hf_errors.RepositoryNotFoundError:
            raise ValueError(
                f"\n🚨 The model for the language pair "
                f"'{self.SRC_LANG}-{self.TGT_LANG}' could not be found. "
                "Ensure the language pair is supported by OpusMT on "
                "Hugging Face (Helsinki-NLP models)."
            )
        except Exception as e:
            raise ValueError(
                f"🚨 An error when verifying the translation model: {str(e)}"
            )

        # Validate silence_threshold (must be greater than 16)
        if self.SILENCE_THRESHOLD <= 16:
            raise ValueError(
                "🚨 'silence_threshold' must be greater than 16 (~ 0.5s). "
            )

        # Validate vad_aggressiveness (must be within the range 0-9)
        if self.VAD_AGGRESSIVENESS < 0 or self.VAD_AGGRESSIVENESS > 9:
            raise ValueError("🚨 'vad_aggressiveness' must be between 0 and 9. ")

        # Validate max_buffer_duration (must be between 5 and 10)
        if self.MAX_BUFFER_DURATION < 5 or self.MAX_BUFFER_DURATION > 10:
            raise ValueError(
                "🚨 'max_buffer_duration' must be between 5 and 10 seconds. "
            )

        # Validate device type
        if self.DEVICE not in ["cpu", "cuda"]:
            raise ValueError("🚨 'device' must be either 'cpu' or 'cuda'.")

        # Validate CUDA availability
        if self.DEVICE == "cuda" and not torch.cuda.is_available():
            raise ValueError(
                "🚨 'cuda' device is not available. "
                "Please use 'cpu' or check your CUDA installation."
            )

        # Validate whisper model
        if self.WHISPER_MODEL not in [
            "tiny",
            "base",
            "small",
            "medium",
            "large",
            "large-v2",
        ]:
            raise ValueError(
                "🚨 'whisper_model' must be one of the following: 'tiny', "
                "'base', 'small', 'medium', 'large', 'large-v2'."
            )

        # Validate translation model
        if self.TRANS_MODEL not in [
            "Helsinki-NLP/opus-mt",
            "Helsinki-NLP/opus-mt-tc-big",
        ]:
            raise ValueError(
                "🚨 'trans_model' must be one of the following: "
                "'Helsinki-NLP/opus-mt', 'Helsinki-NLP/opus-mt-tc-big'. "
            )

        # Validate output method
        if self.OUTPUT not in ["print", "file", "websocket"]:
            raise ValueError(
                "🚨 'output' must be one of the following: 'print', 'file', "
                "'websocket'. "
            )

        # Validate WebSocket port
        if self.OUTPUT == "websocket" and self.WS_PORT is None:
            raise ValueError(
                "🚨 WebSocket port is required for 'websocket' output mode. "
                "Please specify the port using the '--ws_port' argument."
            )

    @property
    def CHUNK_SIZE(self):
        return self._CHUNK_SIZE

    @property
    def SAMPLE_RATE(self):
        return self._SAMPLE_RATE

    @property
    def CHANNELS(self):
        return self._CHANNELS

    @property
    def ENQUEUE_THRESHOLD(self):
        return self._ENQUEUE_THRESHOLD

    @property
    def TRIM_FACTOR(self):
        return self._TRIM_FACTOR

    @property
    def SOFT_SILENCE_THRESHOLD(self):
        return self._SOFT_SILENCE_THRESHOLD

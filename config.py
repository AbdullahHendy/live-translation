# config.py

import torch
import huggingface_hub as hf_hub
import huggingface_hub.errors as hf_errors

class Config:
    """Configuration class for the application."""

    def __init__(self, args):
        """
        Initialize the configuration using parsed CLI arguments.
        """

        # Audio Settings, not all are modifiable for now
        self.CHUNK_SIZE = 512  # 32 ms of audio at 16 kHz
        self.SAMPLE_RATE = 16000  # 16 kHz
        self.CHANNELS = 1  # Mono
        # Audio Processing Settings, not modifiable for now
        # Audio lentgh in seconds to trigger ENQUEUE that is 
        # (send for transcription/translation)
        self.ENQUEUE_THRESHOLD = 1  # seconds
        # Trim audio buffer by this percentage when it 
        # exceeds MAX_BUFFER_DURATION
        self.TRIM_FACTOR = 0.75

        self.args = args
        self._validate_args()

    def _validate_args(self):
        """Validate CLI arguments before applying them."""

        # Validate WebSocket port
        if self.args.output == "websocket" and self.args.ws_port is None:
            raise ValueError(
                "🚨 WebSocket port is required for 'websocket' output mode."
            )

        # Validate CUDA availability
        if self.args.device == "cuda" and not torch.cuda.is_available():
            raise ValueError(
                "🚨 'cuda' device is not available. "
                "Please use 'cpu' or check CUDA installation.")

        # Validate OpusMT translation model and language pair
        model_name = (
            f"{self.args.trans_model_name}-"
            f"{self.args.src_lang}-"
            f"{self.args.tgt_lang}"
        )
        try:
            hf_hub.model_info(model_name)  # Check if the model exists
        except hf_errors.RepositoryNotFoundError:
            raise ValueError(
                f"\n🚨 The language pair "
                f"'{self.args.src_lang}-{self.args.tgt_lang}' "
                "is most likely supported by OpusMT.\n"
                "Check if the language combination exists "
                "on Hugging Face (Helsinki-NLP models)."
            )
        except Exception as e:
            raise ValueError(
                f"🚨 Error in tranlation model."
            )

    def __getattr__(self, name):
        """Allow access to both lowercase and uppercase attributes."""
        lower_name = name.lower()  # Convert to lowercase
        if hasattr(self.args, lower_name):
            return getattr(self.args, lower_name) 
        raise AttributeError(f"Config has no attribute '{name}'")

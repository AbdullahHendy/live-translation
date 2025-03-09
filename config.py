# config.py

import os


class Config:
    """Configuration class for the application."""

    def __init__(self, args: object = None):
        """
        Initialize the configuration with default values. Also allow for 
        dynamic configuration using command-line arguments. 
        """

        # Audio Settings, not all are modifiable for now
        self.CHUNK_SIZE = 512  # 32 ms of audio at 16 kHz
        self.SAMPLE_RATE = 16000  # 16 kHz
        self.CHANNELS = 1  # Mono

        # Number of consecutive (512/16000)s silence chunks to trigger SILENCE
        self.SILENCE_THRESHOLD = int(os.getenv("SILENCE_THRESHOLD", 5)) 
        # VAD Aggressiveness (0-9) 
        self.VAD_AGGRESSIVENESS = int(os.getenv("VAD_AGGRESSIVENESS", 8))

        # Model Settings (Whisper and Translation)
        self.DEVICE = os.getenv("DEVICE", "cpu")  # "cuda" or "cpu"
        # Whisper model name (tiny, base, small, medium, large, or large-v2)
        self.WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
        # Translation model name (facebook/m2m100_418M, facebook/m2m100_1.2B)
        self.TRANS_MODEL = os.getenv("TRANS_MODEL", "facebook/m2m100_418M")

        # Language Settings (Source and Target)
        self.SRC_LANG = os.getenv("SRC_LANG", "en")
        self.TARGET_LANG = os.getenv("TARGET_LANG", "es")

        # Output mode (print, file, or websocket)
        self.OUTPUT_MODE = os.getenv("OUTPUT_MODE", "print")
        self.WS_PORT = os.getenv("WS_PORT")

        # Apply CLI overrides if provided
        if args:
            self._apply_cli_args(args)

    def _apply_cli_args(self, args):
        """Override modifiable settings using command-line arguments."""
        if args.silence_threshold is not None:
            self.SILENCE_THRESHOLD = args.silence_threshold
        if args.vad_aggressiveness is not None:
            self.VAD_AGGRESSIVENESS = args.vad_aggressiveness
        if args.device is not None:
            self.DEVICE = args.device
        if args.whisper_model is not None:
            self.WHISPER_MODEL = args.whisper_model
        if args.trans_model_name is not None:
            self.TRANS_MODEL_NAME = args.trans_model_name
        if args.src_lang is not None:
            self.SRC_LANG = args.src_lang
        if args.tgt_lang is not None:
            self.TARGET_LANG = args.tgt_lang
        if args.output is not None:
            self.OUTPUT_MODE = args.output
        if args.ws_port is not None:
            self.WS_PORT = args.ws_port
            

# config.py

# Audio configuration
CHUNK_SIZE = 480  # 30 ms of audio at 16 kHz
SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = 10  # Consecutive silence chunks to trigger SILENCE
VAD_AGGRESSIVENESS = 3

# Model configuration
DEVICE = "cpu"
WHISPER_MODEL = "base"
TRANS_MODEL_NAME = "facebook/m2m100_418M"  # Meta's M2M-100 model

# Language settings
SRC_LANG = "en"           # Source language for transcription
TARGET_LANG = "es"        # Target language for translation

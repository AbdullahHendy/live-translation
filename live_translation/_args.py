# _args.py

import argparse


def get_args():
    """Parse command-line arguments for user-overridable settings."""
    parser = argparse.ArgumentParser(
        description=("Live Translation Pipeline - Configure runtime settings."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Audio Settings
    parser.add_argument(
        "--silence_threshold",
        type=int,
        default=65,
        help=(
            "Number of consecutive 32ms silent chunks to detect SILENCE.\n"
            "SILENCE clears the audio buffer for transcription/translation.\n"
            "NOTE: Minimum value is 16.\n"
            "Default is 65 (~ 2s)."
        ),
    )

    parser.add_argument(
        "--vad_aggressiveness",
        type=int,
        choices=range(10),
        default=8,
        help=(
            "Voice Activity Detection (VAD) aggressiveness level (0-9).\n"
            "Higher values mean VAD has to be more confident to "
            "detect speech vs silence.\n"
            "Default is 8."
        ),
    )

    parser.add_argument(
        "--max_buffer_duration",
        type=int,
        choices=range(5, 11),
        default=7,
        help=(
            "Max audio buffer duration in seconds before trimming it.\n"
            "Default is 7 seconds."
        ),
    )

    # Models Settings
    parser.add_argument(
        "--device",
        type=str,
        choices=["cpu", "cuda"],
        default="cpu",
        help="Device for processing ('cpu', 'cuda').\nDefault is 'cpu'.",
    )

    parser.add_argument(
        "--whisper_model",
        type=str,
        choices=["tiny", "base", "small", "medium", "large", "large-v2"],
        default="base",
        help=(
            "Whisper model size ('tiny', 'base', 'small', 'medium', "
            "'large', 'large-v2').\n"
            "Default is 'base'."
        ),
    )

    parser.add_argument(
        "--trans_model",
        type=str,
        choices=["Helsinki-NLP/opus-mt", "Helsinki-NLP/opus-mt-tc-big"],
        default="Helsinki-NLP/opus-mt",
        help=(
            "Translation model ('Helsinki-NLP/opus-mt', "
            "'Helsinki-NLP/opus-mt-tc-big'). \n"
            "NOTE: Don't include source and target languages here.\n"
            "Default is 'Helsinki-NLP/opus-mt'."
        ),
    )

    # Language Settings
    parser.add_argument(
        "--src_lang",
        type=str,
        default="en",
        help=(
            "Source/Input language for transcription (e.g., 'en', 'fr').\n"
            "Default is 'en'."
        ),
    )

    parser.add_argument(
        "--tgt_lang",
        type=str,
        default="es",
        help=("Target language for translation (e.g., 'es', 'de').\nDefault is 'es'."),
    )

    # Output Settings
    parser.add_argument(
        "--output",
        type=str,
        choices=["print", "file", "websocket"],
        default="print",
        help=(
            "Output method ('print', 'file', 'websocket').\n"
            "  - 'print': Prints transcriptions and translations to stdout.\n"
            "  - 'file': Saves structured JSON data (see below) "
            "in ./transcripts/transcriptions.json.\n"
            "  - 'websocket': Sends structured JSON data (see below)"
            " over WebSocket.\n"
            "JSON format for 'file' and 'websocket':\n"
            "{\n"
            '    "timestamp": "2025-03-06T12:34:56.789Z",\n'
            '    "transcription": "Hello world",\n'
            '    "translation": "Hola mundo"\n'
            "}.\n"
            "Default is 'print'."
        ),
    )

    parser.add_argument(
        "--ws_port",
        type=int,
        help=(
            "WebSocket port for sending transcriptions.\n"
            "Required if --output is 'websocket'."
        ),
    )

    parser.add_argument(
        "--transcribe_only",
        action="store_true",
        help=("Transcribe only mode. No translations are performed."),
    )

    return parser.parse_args()

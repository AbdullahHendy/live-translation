# args.py

import argparse


def get_args():
    """Parse command-line arguments for user-overridable settings."""
    parser = argparse.ArgumentParser(
        description=(
            "Audio Processing Pipeline - Configure runtime settings."
        )
    )

    # Audio Settings
    parser.add_argument(
        "--silence_threshold",
        type=int,
        help=(
            "Number of consecutive 32ms silent chunks to detect SILENCE. "
            "SILENCE triggers sending a 'FULL' audio buffer for "
            "transcription/translation. Default is 5."
        ),
    )
    parser.add_argument(
        "--vad_aggressiveness",
        type=int,
        choices=range(10),
        help=(
            "Voice Activity Detection (VAD) aggressiveness level (0-9). "
            "Higher values are more aggressive. "
            "Higher mean VAD has to be more confident to detect speech. "
            "Default is 8."
        ),
    )

    # Models Settings
    parser.add_argument(
        "--device",
        type=str,
        choices=["cpu", "cuda"],
        help="Device for processing ('cpu', 'cuda'). Default is 'cpu'.",
    )
    parser.add_argument(
        "--whisper_model",
        type=str,
        choices=["tiny", "base", "small", "medium", "large", "large-v2"],
        help=(
            "Whisper model size ('tiny', 'base', 'small', 'medium', "
            "'large', 'large-v2'). Default is 'base'."
        ),
    )
    parser.add_argument(
        "--trans_model_name",
        type=str,
        choices=["facebook/m2m100_418M", "facebook/m2m100_1.2B"],
        help=(
            "Translation model name ('facebook/m2m100_418M', "
            "'facebook/m2m100_1.2B'). Default is 'facebook/m2m100_418M'."
        ),
    )

    # Language Settings
    parser.add_argument(
        "--src_lang",
        type=str,
        help=(
            "Source/Input language for transcription (e.g., 'en', 'fr'). "
            "Default is 'en'."
        ),
    )
    parser.add_argument(
        "--tgt_lang",
        type=str,
        help=(
            "Target language for translation (e.g., 'es', 'de'). "
            "Default is 'es'."
        ),
    )

    # Output Settings
    parser.add_argument(
        "--output",
        type=str,
        choices=["print", "file", "websocket"],
        help=(
            "Output method for transcriptions ('print', 'file', 'websocket'). "
            "  - 'print': Prints transcriptions and translations to the console. "
            "  - 'file': Saves structured JSON data in transcripts/transcriptions.json. "
            "  - 'websocket': Sends structured JSON data over WebSocket. "
            "JSON format for 'file' and 'websocket':"
            "{\n"
            '    "timestamp": "2025-03-06T12:34:56.789Z",'
            '    "transcription": "Hello world",'
            '    "translation": "Hola mundo"'
            "}.\n"
            "Default is 'print'."
        ),
    )

    parser.add_argument(
        "--ws_port",
        type=int,
        help=(
            "WebSocket port for sending transcriptions. "
            "Requied if --output is 'websocket'. "
        ),
    )

    args = parser.parse_args()

    # Validate WebSocket port if provided if output is 'websocket'
    if args.output == "websocket" and args.ws_port is None:
        raise ValueError(
            "WebSocket port is required for 'websocket' output mode.")

    return parser.parse_args()

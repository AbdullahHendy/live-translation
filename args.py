# args.py

import argparse
import torch


def get_args():
    """Parse command-line arguments for user-overridable settings."""
    parser = argparse.ArgumentParser(
        description=(
            "Audio Processing Pipeline - Configure runtime settings."
        ), 
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Audio Settings
    parser.add_argument(
        "--silence_threshold",
        type=int,
        help=(
            "Number of consecutive 32ms silent chunks to detect SILENCE.\n"
            "SILENCE triggers sending a 'FULL' audio buffer for "
            "transcription/translation.\n"
            "Default is 65 (~ 2s)."
        ),
    )

    parser.add_argument(
        "--vad_aggressiveness",
        type=int,
        choices=range(10),
        help=(
            "Voice Activity Detection (VAD) aggressiveness level (0-9).\n"
            "Higher values mean VAD has to be more confident to "
            "detect speech.\n"
            "Default is 8."
        ),
    )

    parser.add_argument(
        "--max_buffer_duration",
        type=int,
        choices=range(5, 11),
        help=(
            "Max audio buffer duration in seconds before cutting 75%% of it.\n"
            "Default is 7 seconds."
        ),
    )

    # Models Settings
    parser.add_argument(
        "--device",
        type=str,
        choices=["cpu", "cuda"],
        help="Device for processing ('cpu', 'cuda').\n"
        "Default is 'cpu'.",
    )
    
    parser.add_argument(
        "--whisper_model",
        type=str,
        choices=["tiny", "base", "small", "medium", "large", "large-v2"],
        help=(
            "Whisper model size ('tiny', 'base', 'small', 'medium', "
            "'large', 'large-v2').\n"
            "Default is 'base'."
        ),
    )

    parser.add_argument(
        "--trans_model_name",
        type=str,
        choices=["facebook/m2m100_418M", "facebook/m2m100_1.2B"],
        help=(
            "Translation model name ('facebook/m2m100_418M', "
            "'facebook/m2m100_1.2B'). \n"
            "Default is 'facebook/m2m100_418M'."
        ),
    )

    # Language Settings
    parser.add_argument(
        "--src_lang",
        type=str,
        help=(
            "Source/Input language for transcription (e.g., 'en', 'fr').\n"
            "Default is 'en'."
        ),
    )
    
    parser.add_argument(
        "--tgt_lang",
        type=str,
        help=(
            "Target language for translation (e.g., 'es', 'de').\n"
            "Default is 'es'."
        ),
    )

    # Output Settings
    parser.add_argument(
        "--output",
        type=str,
        choices=["print", "file", "websocket"],
        help=(
            "Output method ('print', 'file', 'websocket').\n"
            "  - 'print': Prints transcriptions and translations to stdout.\n"
            "  - 'file': Saves structured JSON data (see below) "
            "in transcripts/transcriptions.json.\n"
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
        help=(
            "Transcribe only mode. No translations are performed."
        ),
    )

    args = parser.parse_args()

    # Validate WebSocket port if provided and output is 'websocket'
    if args.output == "websocket" and args.ws_port is None:
        raise ValueError(
            "🚨 WebSocket port is required for 'websocket' output mode."
        )
    
    # Validate device cuda availability if device is 'cuda'
    if args.device == "cuda" and not torch.cuda.is_available():
        raise ValueError(
            "🚨 'cuda' device is not available. Please use 'cpu' or "
            "make sure the enviroment has CUDA support."
        )

    return parser.parse_args()

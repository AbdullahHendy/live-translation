# _args.py

import argparse


def get_args():
    """Parse command-line arguments for server user-overridable settings."""
    parser = argparse.ArgumentParser(
        description=("Live Translation Server - Configure runtime settings."),
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
        choices=[
            "tiny",
            "base",
            "small",
            "medium",
            "large",
            "large-v2",
            "large-v3",
            "large-v3-turbo",
        ],
        default="base",
        help=(
            "Whisper model size ('tiny', 'base', 'small', 'medium', "
            "'large', 'large-v2', 'large-v3', 'large-v3-turbo). \n"
            "NOTE: Running large models like 'large-v3', or 'large-v3-turbo' "
            "might require a decent GPU with CUDA support for reasonable performance. "
            "\n"
            "NOTE: large-v3-turbo has great accuracy while being significantly faster "
            "than the original large-v3 model. see: "
            "https://github.com/openai/whisper/discussions/2363 \n"
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

    # Logging Settings
    parser.add_argument(
        "--log",
        type=str,
        choices=["print", "file"],
        default=None,
        help=(
            "Optional logging mode for saving transcription output.\n"
            "  - 'file': Save each result to a structured .jsonl file in "
            "./transcripts/transcript_{TIMESTAMP}.jsonl.\n"
            "  - 'print': Print each result to stdout.\n"
            "Default is None (no logging)."
        ),
    )

    parser.add_argument(
        "--ws_port",
        type=int,
        default=8765,
        help=(
            "WebSocket port the of the server.\n"
            "Used to listen for client audio and publish output (e.g., 8765)."
        ),
    )

    parser.add_argument(
        "--transcribe_only",
        action="store_true",
        help=("Transcribe only mode. No translations are performed."),
    )

    # Version
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version and exit.",
    )

    return parser.parse_args()

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
            "Number of consecutive 30ms silent chunks before detecting "
            "SILENCE. SILENCE triggers sending a 'FULL' audio buffer for "
            "transcription/translation. Default is 10."
        ),
    )
    parser.add_argument(
        "--vad_aggressiveness",
        type=int,
        choices=[0, 1, 2, 3],
        help=(
            "Voice Activity Detection (VAD) aggressiveness level (0-3). "
            "Higher values are more aggressive. Default is 3."
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

    return parser.parse_args()

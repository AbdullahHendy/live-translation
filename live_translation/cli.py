# cli.py

from .app import LiveTranslationApp
from .config import Config
from ._args import get_args


def main():
    """CLI entry point."""

    args = get_args()

    # Define the configuration object based on CLI arguments
    cfg = Config(
        device=args.device,
        whisper_model=args.whisper_model,
        trans_model=args.trans_model,
        src_lang=args.src_lang,
        tgt_lang=args.tgt_lang,
        output=args.output,
        ws_port=args.ws_port,
        silence_threshold=args.silence_threshold,
        vad_aggressiveness=args.vad_aggressiveness,
        max_buffer_duration=args.max_buffer_duration,
        transcribe_only=args.transcribe_only,
    )

    # Run the app with the CLI configuration
    app = LiveTranslationApp(cfg)
    app.run()


if __name__ == "__main__":
    main()

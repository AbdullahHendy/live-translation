# client/_args.py

import argparse


def get_args():
    """Parse command-line arguments for the Live Translation Client."""
    parser = argparse.ArgumentParser(
        description="Live Translation Client - Stream audio to the server.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--server",
        type=str,
        help="WebSocket URI of the server (e.g., ws://localhost:8765)",
    )

    parser.add_argument(
        "--codec",
        type=str,
        choices=["pcm", "opus"],
        default="opus",
        help=(
            "Audio codec for WebSocket communication ('pcm', 'opus').\n"
            "Default is 'opus'."
        ),
    )

    # Version
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version and exit.",
    )

    return parser.parse_args()

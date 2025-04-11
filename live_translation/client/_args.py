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
        required=True,
        help="WebSocket URI of the server (e.g., ws://localhost:8765)",
    )

    return parser.parse_args()

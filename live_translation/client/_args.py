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

    # Version
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version and exit.",
    )

    return parser.parse_args()

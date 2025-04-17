# client/cli.py

from live_translation import __version__ as package_version
from .config import Config
from .client import LiveTranslationClient
from ._args import get_args


def print_output(entry):
    print(f"📝 {entry.get('transcription', '')}")
    if entry.get("translation"):
        print(f"🌍 {entry['translation']}")


def main():
    args = get_args()

    if args.version:
        print("live-translate-client ", package_version)
        return

    cfg = Config(server_uri=args.server)
    client = LiveTranslationClient(cfg)

    client.run(callback=print_output)


if __name__ == "__main__":
    main()

# live_translation/tools/demo.py

import asyncio
from live_translation.server.config import Config as ServerConfig
from live_translation.client.config import Config as ClientConfig
from live_translation.server.server import LiveTranslationServer
from live_translation.client.client import LiveTranslationClient


def print_output(entry):
    print(f"📝 {entry.get('transcription', '')}")
    if entry.get("translation"):
        print(f"🌍 {entry['translation']}")


async def async_main():
    # Default configs
    server_cfg = ServerConfig()
    client_cfg = ClientConfig(server_uri=f"ws://localhost:{server_cfg.WS_PORT}")

    server = LiveTranslationServer(server_cfg)
    client = LiveTranslationClient(client_cfg)

    # Start server (non-blocking)
    # server.run(blocking=False) is not awaitable. asyncio.create_task cannot be used.
    server_task = asyncio.to_thread(server.run, blocking=False)

    # Start client (non-blocking)
    client_task = asyncio.create_task(client.run(callback=print_output, blocking=False))

    # Run server and client concurrently
    try:
        # Run both concurrently
        await asyncio.gather(server_task, client_task)
    finally:
        print("\n🛑 Shutting down server and client...")
        server.stop()
        client.stop()


def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

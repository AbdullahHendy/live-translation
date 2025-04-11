import asyncio
from live_translation.server.server import LiveTranslationServer
from live_translation.server.config import Config as ServerConfig
from live_translation.client.client import LiveTranslationClient
from live_translation.client.config import Config as ClientConfig

WS_PORT = 8765
MAGIC_WORD = "TE QUIERO"


async def main():
    # 1. Start server in async/non-blocking mode
    server_cfg = ServerConfig(ws_port=WS_PORT)
    server = LiveTranslationServer(server_cfg)
    pipeline = server.run(blocking=False)

    # 2. Define the callback
    def callback(entry):
        transcription = entry.get("transcription", "")
        translation = entry.get("translation", "")
        print(f"📝 {transcription}")
        print(f"🌍 {translation}")
        if MAGIC_WORD.lower() in translation.lower():
            print("------------------------------")
            print("🎉 Magic word detected! 🙊🙊🙊")
            print("------------------------------")
            return True  # trigger client to stop

    # 3. Run client until magic word is found
    client_cfg = ClientConfig(server_uri=f"ws://localhost:{WS_PORT}")
    client = LiveTranslationClient(client_cfg)
    await client.run(callback=callback, blocking=False)

    print("IM HERE")

    # 4. Shut down server
    pipeline.stop()
    print("🛑 Server stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Shutting down...")

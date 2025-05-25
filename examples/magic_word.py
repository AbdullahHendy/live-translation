import asyncio
from live_translation import LiveTranslationServer, ServerConfig
from live_translation import LiveTranslationClient, ClientConfig

WS_PORT = 8765
MAGIC_WORD = "TE QUIERO"


async def main():
    # 1. Start server in async/non-blocking mode
    server_cfg = ServerConfig(ws_port=WS_PORT)
    server = LiveTranslationServer(server_cfg)
    # server.run(blocking=False) is not awaitable. asyncio.create_task cannot be used.
    server_task = asyncio.to_thread(server.run, blocking=False)

    # 2. Define the callback
    def find_magic_word(entry):
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
    client_task = asyncio.create_task(
        client.run(callback=find_magic_word, blocking=False)
    )

    # 4. Run server and client concurrently
    try:
        # Run both concurrently
        await asyncio.gather(server_task, client_task)
    finally:
        print("\n🛑 Shutting down server and client...")
        server.stop()
        client.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

import multiprocessing as mp
import signal
import os
import sys
import asyncio
import json
import websockets
from live_translation.app import LiveTranslationApp
from live_translation.config import Config

WS_PORT = 8765
MAGIC_WORD = "TE QUIERO"


def run_app():
    cfg = Config(output="websocket", ws_port=WS_PORT)
    app = LiveTranslationApp(cfg)
    app.run()


def shutdown(app_proc):
    if app_proc.is_alive():
        os.kill(app_proc.pid, signal.SIGINT)
        app_proc.join()
    sys.exit(0)


async def listen_for_magic_word(app_proc):
    uri = f"ws://localhost:{WS_PORT}"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    translation = data.get("translation", "")
                    if MAGIC_WORD.lower() in translation.lower():
                        print("------------------------------")
                        print("🎉 Magic word detected! 🙊🙊🙊")
                        print("------------------------------")
                        shutdown(app_proc)
        except (ConnectionRefusedError, websockets.exceptions.ConnectionClosedError):
            await asyncio.sleep(2)


def main():
    app_proc = mp.Process(target=run_app)
    app_proc.start()

    # Signal handler
    def handle_sigterm(signum, frame):
        shutdown(app_proc)

    signal.signal(signal.SIGTERM, handle_sigterm)

    try:
        asyncio.run(listen_for_magic_word(app_proc))
    except KeyboardInterrupt:
        shutdown(app_proc)


if __name__ == "__main__":
    main()

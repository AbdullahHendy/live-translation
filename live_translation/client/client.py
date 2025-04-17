# clinet/client.py

import asyncio
import websockets
import pyaudio
import json
from .config import Config


class LiveTranslationClient:
    """
    Streams audio to a server over WebSocket and handles transcribed output.
    Users can pass a callback to receive each server result.
    Automatically retries connection if server is unavailable.
    Allows programmatic exit via callback return value.
    """

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._exit_requested = False

    async def _send_audio(self, websocket):
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=self.cfg.CHANNELS,
            rate=self.cfg.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.cfg.CHUNK_SIZE,
        )

        print("🎤 Mic open, streaming to server...")
        try:
            while not self._exit_requested:
                data = stream.read(self.cfg.CHUNK_SIZE, exception_on_overflow=False)
                await websocket.send(data)
                await asyncio.sleep(0.01)
        except Exception as e:
            print(f"🚨 Audio send error: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
            print("\n🛑 Audio streaming stopped.")

    async def _receive_output(
        self, websocket, callback, callback_args, callback_kwargs
    ):
        try:
            async for message in websocket:
                try:
                    entry = json.loads(message)
                    if callback:
                        should_stop = callback(
                            entry,
                            *(callback_args or ()),
                            **(callback_kwargs or {}),
                        )
                        if should_stop is True:
                            print("🛑 Callback requested client stopping.")
                            self.stop()
                            break
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse server message: {e}")
        except websockets.ConnectionClosed as e:
            print(f"🔌 WebSocket closed: {e}")

    def run(self, callback, callback_args=(), callback_kwargs=None, blocking=True):
        async def _connect_loop():
            while not self._exit_requested:
                try:
                    print(f"🌐 Connecting to {self.cfg.SERVER_URI}...")
                    async with websockets.connect(self.cfg.SERVER_URI) as websocket:
                        print("✅ Connected to server.")
                        await asyncio.gather(
                            self._send_audio(websocket),
                            self._receive_output(
                                websocket, callback, callback_args, callback_kwargs
                            ),
                        )
                except Exception as e:
                    print(f"🔌 Connection failed: {e}. Retrying in 2 seconds...")
                    await asyncio.sleep(2)

        if blocking:
            try:
                asyncio.run(_connect_loop())
            except KeyboardInterrupt:
                pass
        else:
            return _connect_loop()

    def stop(self):
        """Request the client to stop streaming."""
        print("🛑 Stopping client...")
        self._exit_requested = True

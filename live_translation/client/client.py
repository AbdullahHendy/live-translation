# clinet/client.py

import asyncio
import time
import websockets
import pyaudio
import json
from .config import Config
from .._audio._codec import OpusCodec


class LiveTranslationClient:
    """
    Streams audio to a server over WebSocket and handles transcribed output.
    Users can pass a callback to receive each server result.
    Automatically retries connection if server is unavailable.
    Allows programmatic exit via callback return value.
    """

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.opus = OpusCodec(self.cfg) if self.cfg.CODEC == "opus" else None
        self._exit_requested = False

    async def _send_audio(self, websocket):
        stream = None
        pa = None

        try:
            pa = pyaudio.PyAudio()
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=self.cfg.CHANNELS,
                rate=self.cfg.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.cfg.CHUNK_SIZE,
            )

            print("🎤 Mic open, streaming to server...")

            while not self._exit_requested:
                data = stream.read(self.cfg.CHUNK_SIZE, exception_on_overflow=False)
                # If using Opus codec, encode the audio data from PCM to Opus format
                if self.opus:
                    try:
                        data = self.opus.encode(data)
                    except Exception as e:
                        print(f"🚨 Opus encoding error: {e}")

                await websocket.send(data)
                await asyncio.sleep(0.01)
        except Exception as e:
            print(f"🚨 Audio streaming error: {e}")
            raise AudioCaptureError(f"Audio streaming error: {e}")
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            if pa:
                pa.terminate()
            print("🛑 Audio streaming stopped.")

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
            raise ServerDisconnected("WebSocket connection closed by server.")

    def run(self, callback, callback_args=(), callback_kwargs=None, blocking=True):
        async def _connect_loop():
            while not self._exit_requested:
                try:
                    print(f"🌐 Connecting to {self.cfg.SERVER_URI}...")
                    async with websockets.connect(self.cfg.SERVER_URI) as websocket:
                        # First thing to do is ping to check if the connection is alive.
                        # This is useful to check if the server closed the connection in
                        # the case of a second client trying to connect
                        await websocket.ping()

                        print("✅ Connected to server.")
                        # Use asyncio.TaskGroup instead of asyncio.gather
                        # for better error handling and cancellation. See:
                        # https://docs.python.org/3/library/asyncio-task.html#running-tasks-concurrently # noqa: E501
                        try:
                            async with asyncio.TaskGroup() as tg:
                                tg.create_task(self._send_audio(websocket))
                                tg.create_task(
                                    self._receive_output(
                                        websocket,
                                        callback,
                                        callback_args,
                                        callback_kwargs,
                                    )
                                )

                        # Exit client on audio capture errors and unexpected errors
                        except* ServerDisconnected as eg:
                            print(
                                f"🔌 Disconnected from server during streaming: "
                                f"{eg.exceptions[0]}"
                            )
                        except* AudioCaptureError as eg:
                            print(
                                f"🚨 Audio capture error during streaming: "
                                f"{eg.exceptions[0]}"
                            )
                            self.stop()
                        except* Exception as eg:
                            print(
                                f"🚨 Unexpected error during streaming: "
                                f"{eg.exceptions[0]}"
                            )
                            self.stop()

                except websockets.ConnectionClosedError as e:
                    print(f"🔌 Connection failed: {e.rcvd}.")
                    return
                except Exception as e:
                    print(f"🔌 Connection failed: {e}. Retrying in 2 seconds...")
                    await asyncio.sleep(2)

        if blocking:
            try:
                asyncio.run(_connect_loop())
            except KeyboardInterrupt:
                self.stop()
        else:
            return _connect_loop()

    def stop(self):
        """Request the client to stop streaming."""
        if self._exit_requested:
            # If already stopping, do nothing
            # One use case is in examples/magic_word.py. stop() is called
            # when the magic word is detected, then in the finally block causing stop()
            # to be called again. The stop() in the finally block is needed in the case
            # of KeyboardInterrupt.
            return
        print("🛑 Stopping client...")
        # Allow time for server to flush any remaining queues, preventing the scenario
        # where a new client connects while the server is still flushing old queues.
        time.sleep(2)
        self._exit_requested = True


class ServerDisconnected(Exception):
    """Raised when the WebSocket is closed by the server side."""

    # See: https://docs.python.org/3/library/asyncio-task.html#terminating-a-task-group
    pass


class AudioCaptureError(Exception):
    """Raised when the mic stream fails from client side."""

    # See: https://docs.python.org/3/library/asyncio-task.html#terminating-a-task-group
    pass

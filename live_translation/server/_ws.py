# _ws.py

import asyncio
import threading
import json
import time
import numpy as np
import websockets
from ._logger import OutputLogger
from .._audio._codec import OpusCodec


class WebSocketIO(threading.Thread):
    """
    WebSocket handler for a single client.
    - Receives audio from the client and pushes to audio_queue
    - Sends transcription/translation from output_queue to client
    - Optionally logs output to file or print
    """

    def __init__(self, port, audio_queue, output_queue, stop_event, cfg):
        super().__init__()
        self._port = port
        self._audio_queue = audio_queue
        self._output_queue = output_queue
        self._stop_event = stop_event
        self._loop = None
        self._logger = OutputLogger(cfg) if cfg.LOG else None
        self._opus = OpusCodec(cfg) if cfg.CODEC == "opus" else None
        self._connection_lock = asyncio.Lock()

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        while not self._stop_event.is_set():
            try:
                self._loop.run_until_complete(self._start_server())
                break  # break if successful
            except Exception as e:
                print(f"🚨 WebSocketIO error: {e}. Retrying in 2 seconds...")
                time.sleep(2)

    async def _start_server(self):
        async def handler(websocket):
            # Helper functions to handle audio reception, output sending, and heartbeat
            async def receive_audio():
                try:
                    async for message in websocket:
                        if isinstance(message, bytes):
                            # Decode the audio message if opus codec is used
                            if self._opus:
                                try:
                                    pcm_bytes = self._opus.decode(message)
                                    audio = np.frombuffer(pcm_bytes, dtype=np.int16)
                                except Exception as e:
                                    print(f"🚨 WebSocketIO: Opus decode error: {e}")
                            else:
                                # Default to raw PCM audio
                                audio = np.frombuffer(message, dtype=np.int16)

                            self._audio_queue.put(audio)
                except Exception as e:
                    print(f"🚨 WebSocketIO: receive_audio() error: {e}")

            async def send_output():
                try:
                    while not self._stop_event.is_set():
                        if not self._output_queue.empty():
                            entry = self._output_queue.get()
                            try:
                                await websocket.send(
                                    json.dumps(entry, ensure_ascii=False)
                                )
                                if self._logger:
                                    self._logger.write(entry)
                            except websockets.ConnectionClosed:
                                print(
                                    "🚨 WebSocketIO: Trying to send output on "
                                    "a closed connection"
                                )
                                break
                        await asyncio.sleep(0.01)
                except Exception as e:
                    print(f"🚨 WebSocketIO: send_output() error: {e}")

            async def heartbeat():
                try:
                    while not self._stop_event.is_set():
                        await websocket.ping()
                        await asyncio.sleep(5)
                except websockets.ConnectionClosed:
                    raise ClientDisconnected("Client disconnected during heartbeat")

            # Handler logic starts here
            if self._connection_lock.locked():
                print("🔒 WebSocketIO: Rejecting extra client.")
                await websocket.close(
                    code=1008, reason="\033[91mOnly one client allowed!\033[0m"
                )
                return

            async with self._connection_lock:
                print("🔌 WebSocketIO: Client connected.")

                # Use asyncio.TaskGroup instead of asyncio.gather
                # for better error handling and cancellation. See:
                # https://docs.python.org/3/library/asyncio-task.html#running-tasks-concurrently # noqa: E501
                try:
                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(receive_audio())
                        tg.create_task(send_output())
                        tg.create_task(heartbeat())

                except* ClientDisconnected:
                    print("🔌 WebSocketIO: Client disconnected during operation.")

                except* Exception as e:
                    print(f"🚨 WebSocketIO handler error: {e}")

                # Cleanup: flush queues on disconnect or error
                self._flush_queues()

        # Start the WebSocket server and log immediately after successful bind
        server = None
        try:
            server = await websockets.serve(handler, "0.0.0.0", self._port)
            print(
                f"🌐 WebSocketIO: Listening on \033[91mws://0.0.0.0:{self._port}\033[0m"
            )
            async with server:
                while not self._stop_event.is_set():
                    await asyncio.sleep(0.1)
        finally:
            if server:
                server.close()
                await server.wait_closed()

    def _flush_queues(self):
        """Flush the audio and output queues."""
        print("🧹 Flushing queues...")
        while not self._output_queue.empty():
            self._output_queue.get()
        while not self._audio_queue.empty():
            self._audio_queue.get()
        print("🧹 Queues flushed.")


class ClientDisconnected(Exception):
    """Exception raised when a client disconnects during a WebSocket operation."""

    # For why this is done, see:
    # https://docs.python.org/3/library/asyncio-task.html#terminating-a-task-group
    pass

# ws_server.py

import asyncio
import multiprocessing
import websockets


class WebSocketServer:
    """Handles WebSocket communication in a separate process."""

    def __init__(self, port: int):
        """Initialize WebSocket Server."""
        self.port = port
        self.process = None
        self.queue = multiprocessing.Queue()

    def start(self):
        """Start WebSocket server in a separate process."""
        self.process = multiprocessing.Process(
            target=self._run_server, args=(self.queue, self.port)
        )
        self.process.start()

    def send(self, message):
        """Enqueue a message to be sent to all clients."""
        self.queue.put(message)

    def stop(self):
        """Stop WebSocket server process."""
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join()
            print("🛑 WebSocket server stopped.")

    @staticmethod
    def _run_server(queue, port):
        """WebSocket server loop."""
        try:
            asyncio.run(WebSocketServer._websocket_server(queue, port))
        except KeyboardInterrupt:
            print("🛑 WebSocket server process interrupted")

    @staticmethod
    async def _websocket_server(queue, port):
        """WebSocket server to send structured entries to connected clients."""
        clients = set()

        async def handler(websocket):
            """Handles multiple WebSocket connections."""
            clients.add(websocket)
            print(
                f"🌐 WebSocket Server: Client connected. "
                f"{len(clients)} total clients."
            )
            try:
                await websocket.wait_closed()
            finally:
                clients.remove(websocket)

        try:
            print(f"🌐 WebSocket Server: Listening on ws://localhost:{port}")
            server = await websockets.serve(handler, "localhost", port)

            async def send_messages():
                """Send messages from the queue to all clients."""
                while True:
                    if not queue.empty():
                        message = queue.get()
                        print(f"🌍 Broadcasting to {len(clients)} clients.")
                        if clients:
                            await asyncio.gather(
                                *[client.send(message) for client in clients]
                            )
                    await asyncio.sleep(0.1)

            await asyncio.gather(server.wait_closed(), send_messages())

        except asyncio.CancelledError:
            print("🛑 WebSocket server shutting down...")
        finally:
            server.close()
            await server.wait_closed()

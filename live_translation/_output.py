# _output.py

import os
import json
import threading
import queue
from ._ws import WebSocketServer
from . import config


class OutputManager(threading.Thread):
    """
    Central output thread that pulls from a queue and routes messages
    to print, file, or WebSocket based on config.
    """

    def __init__(
        self, cfg: config.Config, output_queue: queue.Queue, stop_event: threading.Event
    ):
        super().__init__()
        self._cfg = cfg
        self._queue = output_queue
        self._stop_event = stop_event

        self._mode = cfg.OUTPUT
        self._file_path = None
        self._file = None
        self._ws_server = None
        self._ws_port = cfg.WS_PORT

        if self._mode == "file":
            self._file_path = self._next_available_filename_path()
            self._init_file()
            self._file = open(self._file_path, "r+", encoding="utf-8")

        elif self._mode == "websocket":
            self._ws_server = WebSocketServer(self._ws_port)
            self._ws_server.start()

    def run(self):
        print("🧵 OutputManager: Running...")
        try:
            while not (self._stop_event.is_set() and self._queue.empty()):
                try:
                    entry = self._queue.get(timeout=0.5)
                    self._handle_entry(entry)
                except queue.Empty:
                    continue
        finally:
            self._cleanup()
            print("🧵 OutputManager: Stopped.")

    def _handle_entry(self, entry):
        if self._mode == "print":
            print(f"📝 Transcriber: {entry['transcription']}")
            print(f"🌍 Translator: {entry['translation']}")
        elif self._mode == "file" and self._file:
            self._write_to_file(entry)
        elif self._mode == "websocket" and self._ws_server:
            self._ws_server.send(json.dumps(entry, ensure_ascii=False))

    def _write_to_file(self, entry):
        try:
            self._file.seek(0)
            try:
                data = json.load(self._file)
            except json.JSONDecodeError:
                data = []
            data.append(entry)
            self._file.seek(0)
            json.dump(data, self._file, indent=4, ensure_ascii=False)
            self._file.truncate()
            print(f"📁 Updated {self._file_path}")
        except Exception as e:
            print(f"🚨 Failed to write to file: {e}")

    def _init_file(self):
        if not os.path.exists(self._file_path):
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _next_available_filename_path(self, directory="transcripts"):
        os.makedirs(directory, exist_ok=True)
        index = 0
        while os.path.exists(os.path.join(directory, f"transcript_{index}.json")):
            index += 1
        return os.path.join(directory, f"transcript_{index}.json")

    def _cleanup(self):
        if self._file:
            self._file.close()
            print(f"📁 Closed JSON file: {self._file_path}")
        if self._ws_server:
            self._ws_server.stop()

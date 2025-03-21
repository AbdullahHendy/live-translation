# _output.py

import json
import os
from datetime import datetime, timezone
from . import config
from ._ws import WebSocketServer


class OutputManager:
    """
    Handles structured output for transcriptions and translations.
    It can print to console, write to a JSON file, or send over WebSocket.
    """

    def __init__(self, cfg: config.Config):
        """Initialize OutputManager."""
        self._mode = cfg.OUTPUT
        self._file_path = None
        self._file = None
        self._ws_server = None
        self._ws_port = cfg.WS_PORT

        if self._mode == "file":
            self._file_path = self._next_available_filename_path()
            self._init_file()
            self._file = open(self._file_path, "r+")

        elif self._mode == "websocket" and self._ws_port:
            self._ws_server = WebSocketServer(self._ws_port)
            self._ws_server.start()

    def write(self, transcription, translation=""):
        """Write transcriptions and translations based on output mode."""
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = {
            "timestamp": timestamp,
            "transcription": transcription,
            "translation": translation,
        }

        if self._mode == "print":
            print(f"📝 Transcriber: {transcription}")
            print(f"🌍 Translator: {translation}")

        elif self._mode == "file" and self._file:
            self._write_to_file(entry)

        elif self._mode == "websocket" and self._ws_server:
            self._ws_server.send(json.dumps(entry, ensure_ascii=False))

    def close(self):
        """Close resources and stop WebSocket server if it was started."""
        if self._file:
            self._file.close()
            print(f"📁 Closed JSON file: {self._file_path}")

        if self._ws_server:
            self._ws_server.stop()

    def _next_available_filename_path(self, directory="transcripts"):
        """Generate path of a new filename if the current one exists."""
        os.makedirs(directory, exist_ok=True)
        index = 0
        while os.path.exists(os.path.join(directory, f"transcript_{index}.json")):
            index += 1
        return os.path.join(directory, f"transcript_{index}.json")

    def _init_file(self):
        """Initialize file to an empty JSON array."""
        if not os.path.exists(self._file_path):
            with open(self._file_path, "w") as f:
                json.dump([], f)

    def _write_to_file(self, entry):
        """Write a structured entry to a JSON file."""
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

# output_manager.py

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
        self.mode = cfg.OUTPUT
        self.file_path = None
        self.file = None
        self.ws_server = None
        self.ws_port = cfg.WS_PORT

        if self.mode == "file":
            self.file_path = self._next_available_filename_path()
            self._init_file()
            self.file = open(self.file_path, "r+")

        elif self.mode == "websocket" and self.ws_port:
            self.ws_server = WebSocketServer(self.ws_port)
            self.ws_server.start()

    def write(self, transcription, translation=""):
        """Write transcriptions and translations based on output mode."""
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = {
            "timestamp": timestamp,
            "transcription": transcription,
            "translation": translation
        }

        if self.mode == "print":
            print(f"📝 Transcriber: {transcription}")
            print(f"🌍 Translator: {translation}")

        elif self.mode == "file" and self.file:
            self._write_to_file(entry)

        elif self.mode == "websocket" and self.ws_server:
            self.ws_server.send(json.dumps(entry, ensure_ascii=False)) 

    def close(self):
        """Close resources and stop WebSocket server if it was started."""
        if self.file:
            self.file.close()
            print(f"📁 Closed JSON file: {self.file_path}")

        if self.ws_server:
            self.ws_server.stop() 

    def _next_available_filename_path(self, directory="transcripts"):
        """Generate path of a new filename if the current one exists."""
        os.makedirs(directory, exist_ok=True)
        index = 0
        while os.path.exists(
            os.path.join(directory, f"transcript_{index}.json")
        ):
            index += 1
        return os.path.join(directory, f"transcript_{index}.json")

    def _init_file(self):
        """Initialize file to an empty JSON array."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def _write_to_file(self, entry):
        """Write a structured entry to a JSON file."""
        self.file.seek(0)
        try:
            data = json.load(self.file)
        except json.JSONDecodeError:
            data = []

        data.append(entry)

        self.file.seek(0)
        json.dump(data, self.file, indent=4, ensure_ascii=False)
        self.file.truncate()
        print(f"📁 Updated {self.file_path}")

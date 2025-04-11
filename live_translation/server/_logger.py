# live_translation/_logger.py

import os
import json
from datetime import datetime


class OutputLogger:
    """
    Logs transcription/translation results to file or stdout.
    Controlled via cfg.LOG = 'file', 'print', or None.
    """

    def __init__(self, cfg):
        self._mode = cfg.LOG
        self._file = None
        self._file_path = None

        if self._mode == "file":
            self._file_path = self._next_available_path()
            os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
            self._file = open(self._file_path, "a", encoding="utf-8")
            print(f"📁 Logging to: {self._file_path}")

    def write(self, entry: dict):
        if self._mode == "print":
            print(f"📝 {entry['transcription']}")
            print(f"🌍 {entry['translation']}")
        elif self._mode == "file" and self._file:
            json.dump(entry, self._file, ensure_ascii=False)
            self._file.write("\n")
            self._file.flush()

    def close(self):
        if self._file:
            self._file.close()
            print(f"📁 Closed log file: {self._file_path}")

    def _next_available_path(self, directory="transcripts"):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return os.path.join(directory, f"transcript_{timestamp}.jsonl")

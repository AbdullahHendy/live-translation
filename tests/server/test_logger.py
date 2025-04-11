import os
import json
from live_translation.server._logger import OutputLogger
from live_translation.server.config import Config


def test_logger_print(capsys):
    cfg = Config(log="print")
    logger = OutputLogger(cfg)

    entry = {
        "timestamp": "2025-04-10T00:00:00Z",
        "transcription": "Hello",
        "translation": "Hola",
    }
    logger.write(entry)

    captured = capsys.readouterr()
    assert "📝 Hello" in captured.out, (
        "Expected transcription output not found in captured stdout."
    )
    assert "🌍 Hola" in captured.out, (
        "Expected translation output not found in captured stdout."
    )


def test_logger_file():
    cfg = Config(log="file")
    logger = OutputLogger(cfg)

    entry = {
        "timestamp": "2025-04-10T00:00:00Z",
        "transcription": "Hello",
        "translation": "Hola",
    }
    logger.write(entry)
    logger.close()

    path = logger._file_path
    assert os.path.exists(path)

    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    last = json.loads(lines[-1])
    assert last["transcription"] == "Hello"
    assert last["translation"] == "Hola"

    os.remove(path)

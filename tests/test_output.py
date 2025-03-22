import asyncio
import glob
import json
import os
import time
import pytest
import websockets
import threading
import multiprocessing as mp
from live_translation._output import OutputManager
from live_translation.config import Config


@pytest.fixture
def stop_event():
    return threading.Event()


@pytest.fixture
def output_queue():
    return mp.Queue()


@pytest.fixture
def temp_config():
    return Config(output="print")


def test_output_print(capsys, temp_config, output_queue, stop_event):
    output_manager = OutputManager(temp_config, output_queue, stop_event)
    output_manager.start()

    entry = {
        "timestamp": "2025-03-21T00:00:00Z",
        "transcription": "Hello",
        "translation": "Hola",
    }
    output_queue.put(entry)

    time.sleep(2)

    stop_event.set()
    output_manager.join()

    captured = capsys.readouterr()
    assert "📝 Transcriber: Hello" in captured.out, (
        "Output should contain 📝 Transcriber: Hello"
    )
    assert "🌍 Translator: Hola" in captured.out, (
        "Output should container 🌍 Translator: Hola"
    )


def test_output_file(output_queue, stop_event):
    cfg = Config(output="file")
    output_manager = OutputManager(cfg, output_queue, stop_event)
    output_manager.start()

    entry = {
        "timestamp": "2025-03-21T00:00:00Z",
        "transcription": "Hello",
        "translation": "Hola",
    }
    output_queue.put(entry)

    time.sleep(2)

    stop_event.set()
    output_manager.join()

    latest_file = find_latest_transcript()
    assert latest_file is not None

    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) > 0
    assert data[-1]["transcription"] == "Hello"
    assert data[-1]["translation"] == "Hola"

    os.remove(latest_file)


@pytest.mark.asyncio
async def test_output_websocket(output_queue, stop_event):
    cfg = Config(output="websocket", ws_port=8765)
    output_manager = OutputManager(cfg, output_queue, stop_event)
    output_manager.start()

    # Wait for WebSocket server to be ready
    for _ in range(10):
        try:
            ws = await websockets.connect(f"ws://localhost:{cfg.WS_PORT}")
            break
        except (ConnectionRefusedError, OSError):
            await asyncio.sleep(0.5)
    else:
        pytest.fail("WebSocket server did not start in time")

    entry = {
        "timestamp": "2025-03-21T00:00:00Z",
        "transcription": "Hello",
        "translation": "Hola",
    }
    output_queue.put(entry)

    received_message = await ws.recv()
    data = json.loads(received_message)
    assert data["transcription"] == "Hello"
    assert data["translation"] == "Hola"

    await ws.close()
    stop_event.set()
    output_manager.join()


def find_latest_transcript():
    transcript_files = glob.glob("transcripts/transcript_*.json")
    if not transcript_files:
        return None
    return max(transcript_files, key=os.path.getctime)

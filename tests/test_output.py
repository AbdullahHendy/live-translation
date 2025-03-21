import asyncio
import glob
import json
import os
import pytest
import websockets
from live_translation._output import OutputManager
from live_translation.config import Config


@pytest.fixture
def temp_config():
    """Fixture to create a Config instance with default values."""
    return Config(output="print")


def test_output_print(capsys, temp_config):
    """Test if OutputManager prints correctly to stdout."""
    output_manager = OutputManager(temp_config)
    output_manager.write("Hello", "Hola")

    captured = capsys.readouterr()
    assert "📝 Transcriber: Hello" in captured.out
    assert "🌍 Translator: Hola" in captured.out


def test_output_file(temp_config):
    """Test if OutputManager writes correctly to a JSON file."""
    temp_config.OUTPUT = "file"
    output_manager = OutputManager(temp_config)

    output_manager.write("Hello", "Hola")

    latest_file = find_latest_transcript()
    assert latest_file is not None, "No transcript file was created!"

    with open(latest_file, "r") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["transcription"] == "Hello"
    assert data[0]["translation"] == "Hola"

    os.remove(latest_file)
    assert not os.path.exists(latest_file)


@pytest.mark.asyncio
async def test_output_websocket(temp_config):
    """Test if OutputManager correctly sends messages over WebSocket."""

    temp_config.OUTPUT = "websocket"
    temp_config.WS_PORT = 8765
    output_manager = OutputManager(temp_config)

    for _ in range(5):
        try:
            async with websockets.connect(
                f"ws://localhost:{temp_config.WS_PORT}"
            ) as websocket:
                output_manager.write("Hello", "Hola")
                received_message = await websocket.recv()
                received_data = json.loads(received_message)

                assert received_data["transcription"] == "Hello"
                assert received_data["translation"] == "Hola"
                break
        except ConnectionRefusedError:
            await asyncio.sleep(1)  # Wait for server to start
    else:
        pytest.fail("WebSocket server did not start in time!")

    output_manager.close()


# Helper function
def find_latest_transcript():
    """Find the most recent transcript file in the `transcripts/` directory."""
    transcript_files = glob.glob("transcripts/transcript_*.json")
    if not transcript_files:
        return None
    return max(transcript_files, key=os.path.getctime)

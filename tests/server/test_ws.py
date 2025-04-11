import asyncio
import json
from pathlib import Path
import wave
import numpy as np
import pytest
import websockets
import multiprocessing as mp
from live_translation.server._ws import WebSocketIO
from live_translation.server.config import Config


@pytest.mark.asyncio
async def test_websocketio_end_to_end():
    port = 8877
    stop_event = mp.Event()
    audio_queue = mp.Queue()
    output_queue = mp.Queue()
    cfg = Config(ws_port=port)

    # Start the WebSocketIO thread
    ws_io = WebSocketIO(port, audio_queue, output_queue, stop_event, cfg)
    ws_io.daemon = True
    ws_io.start()

    await asyncio.sleep(0.5)

    uri = f"ws://localhost:{port}"
    async with websockets.connect(uri) as websocket:
        # Load audio and send it
        wav_path = Path("tests/audio_samples/sample.wav")
        assert wav_path.exists(), f"Audio file {wav_path} does not exist"
        with wave.open(str(wav_path), "rb") as wf:
            num_channels = wf.getnchannels()
            frame_rate = wf.getframerate()
            num_frames = wf.getnframes()

            assert frame_rate == 16000, (
                f"Expected 16kHz sample rate, got {frame_rate}Hz"
            )
            assert num_channels == 1, (
                f"Expected mono audio, got {num_channels} channels"
            )

            raw_audio = wf.readframes(num_frames)
            expected_audio = np.frombuffer(raw_audio, dtype=np.int16)

            await websocket.send(raw_audio)

        # Check that audio would be received on the server side
        recv_audio = audio_queue.get(timeout=2)
        assert isinstance(recv_audio, np.ndarray)
        assert recv_audio.dtype == np.int16
        assert recv_audio.shape == expected_audio.shape

        # Mimic sending transcription from server
        entry = {
            "timestamp": "2025-04-10T00:00:00Z",
            "transcription": "Hello, how are you?",
            "translation": "Hola, ¿cómo estás?",
        }
        output_queue.put(entry)

        # Check that client received the output
        msg = await asyncio.wait_for(websocket.recv(), timeout=2)
        decoded = json.loads(msg)
        assert decoded["transcription"] == "Hello, how are you?"
        assert decoded["translation"] == "Hola, ¿cómo estás?"

    stop_event.set()
    ws_io.join(timeout=2)

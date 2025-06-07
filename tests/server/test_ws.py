import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import wave
import numpy as np
import pytest
import websockets
import multiprocessing as mp
from live_translation.server._ws import ClientDisconnected, WebSocketIO
from live_translation.server.config import Config


@pytest.mark.asyncio
async def test_websocketio_end_to_end_pcm():
    port = 8877
    stop_event = mp.Event()
    audio_queue = mp.Queue()
    output_queue = mp.Queue()
    cfg = Config(ws_port=port, codec="pcm")

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


@pytest.mark.asyncio
async def test_websocketio_opus_decode_success():
    port = 8881
    stop_event = mp.Event()
    audio_queue = mp.Queue()
    output_queue = mp.Queue()

    # Mock OpusCodec.decode to return valid PCM bytes
    mock_codec = MagicMock()
    DECODED_SAMPLES = 640
    decoded_bytes = (np.ones(DECODED_SAMPLES, dtype=np.int16)).tobytes()
    mock_codec.decode.return_value = decoded_bytes

    with patch("live_translation.server._ws.OpusCodec", return_value=mock_codec):
        cfg = Config(ws_port=port, codec="opus")

        ws_io = WebSocketIO(port, audio_queue, output_queue, stop_event, cfg)
        ws_io.daemon = True
        ws_io.start()

        await asyncio.sleep(0.5)

        uri = f"ws://localhost:{port}"
        async with websockets.connect(uri) as websocket:
            await websocket.send(b"fake-opus-audio")
            await asyncio.sleep(0.1)

        # Check the decoded audio
        result = audio_queue.get(timeout=2)
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.int16
        assert result.shape == (DECODED_SAMPLES,)
        mock_codec.decode.assert_called_once_with(b"fake-opus-audio")

    stop_event.set()
    ws_io.join(timeout=2)


@pytest.mark.asyncio
async def test_websocketio_opus_decode_error(capfd):
    port = 8882
    stop_event = mp.Event()
    audio_queue = mp.Queue()
    output_queue = mp.Queue()

    # Mock OpusCodec.decode to raise an error
    mock_codec = MagicMock()
    mock_codec.decode.side_effect = RuntimeError("decode failed")

    with patch("live_translation.server._ws.OpusCodec", return_value=mock_codec):
        cfg = Config(ws_port=port, codec="opus")

        ws_io = WebSocketIO(port, audio_queue, output_queue, stop_event, cfg)
        ws_io.daemon = True
        ws_io.start()

        await asyncio.sleep(0.5)

        uri = f"ws://localhost:{port}"
        async with websockets.connect(uri) as websocket:
            await websocket.send(b"bad-opus-audio")
            await asyncio.sleep(0.1)

        # Assert nothing was enqueued
        assert audio_queue.empty()

        # Assert error was printed
        out, _ = capfd.readouterr()
        assert "🚨 WebSocketIO: Opus decode error: decode failed" in out

    stop_event.set()
    ws_io.join(timeout=2)


@pytest.mark.asyncio
async def test_websocketio_reject_extra_clients():
    port = 8898
    stop_event = mp.Event()
    audio_queue = mp.Queue()
    output_queue = mp.Queue()
    cfg = Config(ws_port=port)

    ws_io = WebSocketIO(port, audio_queue, output_queue, stop_event, cfg)
    ws_io.daemon = True
    ws_io.start()

    await asyncio.sleep(0.5)

    uri = f"ws://localhost:{port}"

    # First client connects and holds the lock
    client1 = await websockets.connect(uri)

    # Second client tries to connect and should be rejected
    client2 = await websockets.connect(uri)
    try:
        await asyncio.sleep(0.5)
        await client2.recv()  # Force a read to trigger the close
    except websockets.exceptions.ConnectionClosedError as e:
        assert e.rcvd.code == 1008
        assert "Only one client allowed" in e.rcvd.reason
    else:
        assert False, "Second client was not rejected as expected"

    await client1.close()
    stop_event.set()
    ws_io.join(timeout=2)


@pytest.mark.asyncio
async def test_websocketio_logger_called(capsys):
    port = 8879
    stop_event = mp.Event()
    audio_queue = mp.Queue()
    output_queue = mp.Queue()

    # 👇 Enable logger with print mode
    cfg = Config(ws_port=port, log="print")

    ws_io = WebSocketIO(port, audio_queue, output_queue, stop_event, cfg)
    ws_io.daemon = True
    ws_io.start()

    await asyncio.sleep(0.5)

    uri = f"ws://localhost:{port}"
    async with websockets.connect(uri) as websocket:
        # Put message in output queue → triggers logger.write
        entry = {"transcription": "hello", "translation": "bonjour"}
        output_queue.put(entry)

        # Receive message from server
        msg = await websocket.recv()
        decoded = json.loads(msg)
        assert decoded["transcription"] == "hello"

        out, _ = capsys.readouterr()
        assert "📝 hello" in out
        assert "🌍 bonjour" in out

    stop_event.set()
    ws_io.join(timeout=2)


@pytest.mark.asyncio
async def test_websocketio_client_disconnected(capfd):
    port = 8896
    stop_event = mp.Event()
    audio_queue = mp.Queue()
    output_queue = mp.Queue()
    cfg = Config(ws_port=port)

    async def fake_start_server(self):
        async def handler(_):
            async with self._connection_lock:
                print("🔌 WebSocketIO: Client connected.")
                try:
                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(asyncio.sleep(0))  # receive_audio
                        tg.create_task(asyncio.sleep(0))  # send_output
                        tg.create_task(self._simulate_heartbeat())  # heartbeat
                except* ClientDisconnected:
                    print("🔌 WebSocketIO: Client disconnected during operation.")
                self._flush_queues()

        await handler(None)
        stop_event.set()

    async def _simulate_heartbeat(self):
        raise ClientDisconnected("simulated disconnect")

    ws_io = WebSocketIO(port, audio_queue, output_queue, stop_event, cfg)
    # Override the _start_server method with the fake one.
    # __get__ binds the fake_start_server to the ws_io instance so it receives `self`
    ws_io._start_server = fake_start_server.__get__(ws_io, WebSocketIO)
    # __get__ binds the _simulate_heartbeat to the ws_io instance so it receives `self`
    ws_io._simulate_heartbeat = _simulate_heartbeat.__get__(ws_io, WebSocketIO)
    ws_io.daemon = True
    ws_io.start()

    await asyncio.sleep(1)
    ws_io.join(timeout=2)

    out, _ = capfd.readouterr()
    assert "🔌 WebSocketIO: Client disconnected during operation." in out
    assert "🧹 Flushing queues..." in out
    assert "🧹 Queues flushed." in out


def test_websocketio_flush_queues(capsys):
    port = 89891
    stop_event = mp.Event()
    audio_queue = mp.Queue()
    output_queue = mp.Queue()
    cfg = Config(ws_port=port)

    # Put dummy data into queues
    for _ in range(3):
        audio_queue.put(b"audio")
        output_queue.put({"transcription": "dummy", "translation": "dummy"})

    ws = WebSocketIO(port, audio_queue, output_queue, stop_event, cfg)

    assert not audio_queue.empty()
    assert not output_queue.empty()

    ws._flush_queues()

    # Validate queues are flushed
    assert audio_queue.empty()
    assert output_queue.empty()

    # Capture and check printed output
    out, _ = capsys.readouterr()
    assert "🧹 Flushing queues..." in out
    assert "🧹 Queues flushed." in out

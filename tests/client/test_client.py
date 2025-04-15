import asyncio
import pytest
from unittest import mock
from live_translation.client.client import LiveTranslationClient
from live_translation.client.config import Config


@pytest.fixture
def config():
    return Config(server_uri="ws://localhost:8765")


@pytest.mark.asyncio
async def test_receive_output_callback_exit(config):
    """Test that the client exits when callback returns True."""
    client = LiveTranslationClient(config)

    messages = [
        '{"transcription": "hello", "translation": "hola"}',
        '{"transcription": "i love you", "translation": "te quiero"}',
    ]

    # Mock websocket that simulates receiving messages
    mock_websocket = mock.AsyncMock()
    mock_websocket.__aiter__.return_value = iter(messages)

    called_entries = []

    # Mock callback function with a return value to trigger exit
    def mock_callback(entry):
        called_entries.append(entry)
        return "te quiero" in entry["translation"].lower()

    await client._receive_output(mock_websocket, mock_callback, None, None)

    assert len(called_entries) == 2
    assert client._exit_requested is True


@pytest.mark.asyncio
async def test_receive_output_callback_with_args_kwargs():
    """Test that args and kwargs are passed to the callback and stop is triggered."""
    from live_translation.client.config import Config

    config = Config(server_uri="ws://fake-uri")

    client = LiveTranslationClient(config)

    # Simulated JSON messages from server
    messages = [
        '{"transcription": "hello", "translation": "hola"}',
        '{"transcription": "bye", "translation": "te quiero"}',
    ]

    # Mock websocket that behaves like async iterable
    mock_websocket = mock.AsyncMock()
    mock_websocket.__aiter__.return_value = iter(messages)

    received = []
    callback_args = ("extra1",)
    callback_kwargs = {"flag": "value"}

    def mock_callback(entry, *args, **kwargs):
        received.append((entry, args, kwargs))
        # Trigger stop if Spanish translation is "te quiero"
        return entry["translation"] == "te quiero"

    await client._receive_output(
        mock_websocket,
        callback=mock_callback,
        callback_args=callback_args,
        callback_kwargs=callback_kwargs,
    )

    # Assertions
    assert len(received) == 2
    assert received[0][1] == callback_args
    assert received[0][2] == callback_kwargs
    assert received[1][0]["translation"] == "te quiero"
    assert client._exit_requested is True


@pytest.mark.asyncio
async def test_receive_output_handles_json_error(config):
    """Test that bad JSON doesn't crash the client."""
    client = LiveTranslationClient(config)

    messages = [
        '{"transcription": "hello", "translation": "hola"}',
        "not-a-json",
        '{"transcription": "again", "translation": "otra vez"}',
    ]

    mock_websocket = mock.AsyncMock()
    mock_websocket.__aiter__.return_value = iter(messages)

    seen = []

    def cb(entry):
        seen.append(entry)
        return len(seen) == 2

    await client._receive_output(mock_websocket, cb, None, None)

    assert len(seen) == 2
    assert client._exit_requested


@pytest.mark.asyncio
async def test_send_audio_streams_once(monkeypatch):
    """Test that audio is read and sent once from the microphone."""

    # Setup client with a test config
    cfg = Config(server_uri="ws://localhost:8765")
    client = LiveTranslationClient(cfg)

    # Trick to force early exit after 1 send (not the main use case of _exit_requested)
    client._exit_requested = False

    async def stop_after_delay():
        await asyncio.sleep(0.02)
        client._exit_requested = True

    # Mock PyAudio and stream
    mock_stream = mock.MagicMock()
    mock_stream.read.return_value = b"fake-audio-bytes"

    mock_pa = mock.MagicMock()
    mock_pa.open.return_value = mock_stream

    monkeypatch.setattr("pyaudio.PyAudio", lambda: mock_pa)

    # Mock websocket to collect what was sent
    mock_websocket = mock.AsyncMock()

    asyncio.create_task(stop_after_delay())

    # Method under test
    await client._send_audio(mock_websocket)

    # Assert audio was read
    mock_stream.read.assert_called()
    # Assert something was sent over websocket
    mock_websocket.send.assert_called_with(b"fake-audio-bytes")

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from live_translation.client.client import LiveTranslationClient
from live_translation.client.config import Config


@pytest.fixture
def config():
    return Config(server_uri="ws://localhost:8764")


@pytest.mark.asyncio
async def test_receive_output_callback_exit(config):
    """Test that the client exits when callback returns True."""
    client = LiveTranslationClient(config)

    messages = [
        '{"transcription": "hello", "translation": "hola"}',
        '{"transcription": "i love you", "translation": "te quiero"}',
    ]

    # Mock websocket that simulates receiving messages
    mock_websocket = AsyncMock()
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
    mock_websocket = AsyncMock()
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

    mock_websocket = AsyncMock()
    mock_websocket.__aiter__.return_value = iter(messages)

    seen = []

    def cb(entry):
        seen.append(entry)
        return len(seen) == 2

    await client._receive_output(mock_websocket, cb, None, None)

    assert len(seen) == 2
    assert client._exit_requested


@pytest.mark.asyncio
async def test_send_audio_streams_once():
    """Test that audio is read and sent once from the microphone when using PCM."""

    # Set up mocks
    mock_stream = MagicMock()
    mock_stream.read.return_value = b"fake-audio-bytes"

    mock_pa = MagicMock()
    mock_pa.open.return_value = mock_stream

    mock_websocket = AsyncMock()

    # Patch before client instantiation
    with patch("pyaudio.PyAudio", return_value=mock_pa):
        cfg = Config(server_uri="ws://localhost:8764", codec="pcm")
        client = LiveTranslationClient(cfg)

        # Force early exit after first send
        async def send_side_effect(data):
            client._exit_requested = True
            return None

        mock_websocket.send.side_effect = send_side_effect

        await client._send_audio(mock_websocket)

    # Assertions
    mock_stream.read.assert_called_once()
    mock_websocket.send.assert_called_once_with(b"fake-audio-bytes")


@pytest.mark.asyncio
async def test_send_audio_opus_encoding():
    """Test that Opus codec is used and encode() is called when codec is 'opus'."""

    # Setup mocks
    mock_codec = MagicMock()
    mock_codec.encode.return_value = b"encoded-audio"

    mock_stream = MagicMock()
    mock_stream.read.return_value = b"pcm-audio"

    mock_pa = MagicMock()
    mock_pa.open.return_value = mock_stream

    mock_websocket = AsyncMock()

    # Patch OpusCodec and PyAudio before instantiation
    with (
        patch("live_translation.client.client.OpusCodec", return_value=mock_codec),
        patch("pyaudio.PyAudio", return_value=mock_pa),
    ):
        cfg = Config(server_uri="ws://localhost:8765", codec="opus")
        client = LiveTranslationClient(cfg)

        # Make websocket.send() stop the loop after first call
        async def send_side_effect(data):
            client._exit_requested = True
            return None

        mock_websocket.send.side_effect = send_side_effect

        await client._send_audio(mock_websocket)

    # Assertions
    mock_codec.encode.assert_called_once_with(b"pcm-audio")
    mock_websocket.send.assert_called_once_with(b"encoded-audio")


@pytest.mark.asyncio
async def test_audio_opus_encoding_exception(capfd):
    """Test that Opus encoding errors are caught and logged."""

    # Setup mocks
    mock_codec = MagicMock()
    mock_codec.encode.side_effect = RuntimeError("fake encoding failure")

    mock_stream = MagicMock()
    mock_stream.read.return_value = b"pcm-audio"

    mock_pa = MagicMock()
    mock_pa.open.return_value = mock_stream

    mock_websocket = AsyncMock()

    # Patch before client instantiation
    with (
        patch("live_translation.client.client.OpusCodec", return_value=mock_codec),
        patch("pyaudio.PyAudio", return_value=mock_pa),
    ):
        cfg = Config(server_uri="ws://localhost:8765", codec="opus")
        client = LiveTranslationClient(cfg)

        # Exit after first iteration
        async def send_side_effect(data):
            client._exit_requested = True
            return None

        mock_websocket.send.side_effect = send_side_effect

        await client._send_audio(mock_websocket)

    # Check printed error log
    captured = capfd.readouterr()
    assert "🚨 Opus encoding error: fake encoding failure" in captured.out
    mock_codec.encode.assert_called_once_with(b"pcm-audio")

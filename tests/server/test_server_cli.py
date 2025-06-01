# tests/server/test_server_cli.py

import pytest
from unittest import mock
from live_translation.server import cli
from live_translation import __version__ as package_version


def test_server_cli_prints_version(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["server", "--version"])
    cli.main()
    out, _ = capsys.readouterr()
    assert f"live-translate-server  {package_version}" in out


def test_server_cli_runs_with_defaults(monkeypatch):
    """Test CLI runs with default and required args."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "server",
            "--whisper_model",
            "base",
            "--trans_model",
            "Helsinki-NLP/opus-mt",
            "--src_lang",
            "en",
            "--tgt_lang",
            "es",
            "--log",
            "print",
        ],
    )

    with mock.patch("live_translation.server.cli.LiveTranslationServer") as MockServer:
        instance = MockServer.return_value
        cli.main()
        instance.run.assert_called_once()


def test_server_cli_with_all_args(monkeypatch):
    """Test CLI with all arguments explicitly set."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "server",
            "--device",
            "cpu",
            "--whisper_model",
            "tiny",
            "--trans_model",
            "Helsinki-NLP/opus-mt-tc-big",
            "--src_lang",
            "fr",
            "--tgt_lang",
            "de",
            "--log",
            "file",
            "--ws_port",
            "8888",
            "--silence_threshold",
            "40",
            "--vad_aggressiveness",
            "5",
            "--max_buffer_duration",
            "10",
            "--transcribe_only",
        ],
    )

    with mock.patch("live_translation.server.cli.LiveTranslationServer") as MockServer:
        instance = MockServer.return_value
        cli.main()
        instance.run.assert_called_once()


def test_server_cli_help(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["server", "--help"])
    with pytest.raises(SystemExit):
        cli.main()
    out, _ = capsys.readouterr()
    assert "usage:" in out
    assert "--silence_threshold" in out
    assert "--vad_aggressiveness" in out
    assert "--max_buffer_duration" in out
    assert "--device" in out
    assert "--whisper_model" in out
    assert "--trans_model" in out
    assert "--src_lang" in out
    assert "--tgt_lang" in out
    assert "--log" in out
    assert "--ws_port" in out
    assert "--transcribe_only" in out
    assert "--version" in out


def test_server_cli_invalid_choice(monkeypatch):
    """Test invalid choice for --device raises a SystemExit."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "server",
            "--device",
            "invalid",  # not in ["cpu", "cuda"]
            "--whisper_model",
            "base",
            "--trans_model",
            "Helsinki-NLP/opus-mt",
            "--src_lang",
            "en",
            "--tgt_lang",
            "es",
        ],
    )
    with pytest.raises(SystemExit):
        cli.main()

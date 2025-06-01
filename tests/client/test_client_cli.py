import pytest
from unittest import mock
from live_translation.client import cli
from live_translation import __version__ as package_version


def test_cli_prints_version(monkeypatch, capsys):
    """Test --version flag prints version and exits."""
    monkeypatch.setattr("sys.argv", ["client", "--version"])

    cli.main()

    out, _ = capsys.readouterr()
    assert f"live-translate-client  {package_version}" in out  ## 2 spaces


def test_cli_runs_client(monkeypatch):
    """Test that main() initializes and runs the client."""
    monkeypatch.setattr("sys.argv", ["client", "--server", "ws://localhost:8765"])

    with mock.patch("live_translation.client.cli.LiveTranslationClient") as MockClient:
        instance = MockClient.return_value
        cli.main()
        instance.run.assert_called_once()
        instance.run.assert_called_with(callback=mock.ANY)


def test_cli_print_output(capsys):
    """Test print_output helper function."""
    transcription_only_entry = {"transcription": "hello"}
    translation_entry = {"transcription": "hello", "translation": "hola"}

    cli.print_output(transcription_only_entry)

    transcription_only_out, _ = capsys.readouterr()
    assert "📝 hello" in transcription_only_out
    assert "🌍 hola" not in transcription_only_out

    cli.print_output(translation_entry)
    translation_out, _ = capsys.readouterr()
    assert "📝 hello" in translation_out
    assert "🌍 hola" in translation_out


def test_cli_help(monkeypatch, capsys):
    """Test --help prints usage and exits."""
    monkeypatch.setattr("sys.argv", ["client", "--help"])

    with pytest.raises(SystemExit):
        cli.main()

    out, _ = capsys.readouterr()
    assert "usage:" in out
    assert "--server" in out
    assert "--version" in out


def test_cli_missing_server(monkeypatch):
    """Test CLI exits with error if --server is missing."""
    monkeypatch.setattr("sys.argv", ["client"])  # no --server

    with pytest.raises(ValueError, match="server_uri.*cannot be empty"):
        cli.main()

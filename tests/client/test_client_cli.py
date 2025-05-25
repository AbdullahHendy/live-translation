import os
import subprocess
import select

import pytest

SERVER_COMMAND = [
    "python",
    "-u",
    "-m",
    "live_translation.server.cli",
    "--transcribe_only",
    "--ws_port",
    "8764",
]

CLIENT_COMMAND = [
    "python",
    "-u",
    "-m",
    "live_translation.client.cli",
    "--server",
    "ws://localhost:8764",
]


def test_cli_help():
    """Test if client CLI shows help text."""
    result = subprocess.run(CLIENT_COMMAND + ["--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


def test_cli_invalid_argument():
    """Test that client CLI shows an error for unknown arguments."""
    result = subprocess.run(
        CLIENT_COMMAND + ["--invalid"], capture_output=True, text=True
    )

    assert result.returncode != 0
    assert "unrecognized arguments" in result.stderr.lower() or result.stdout.lower()


def test_cli_no_connection():
    """Test that client attempts to connect and responds accordingly."""
    process = subprocess.Popen(
        CLIENT_COMMAND,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        output = wait_for_output(process, "🔌 Connection failed:", timeout=10)

        assert output, "No connection message was found"

    finally:
        process.terminate()
        process.wait(timeout=5)
        if process.stdout:
            process.stdout.close()


@pytest.mark.skipif(
    os.environ.get("CI") == "true",
    reason="Skipping full client-server test on CI due to PyAudio hardware dependency",
)
def test_cli_connection():
    # Start the server
    server_proc = subprocess.Popen(
        SERVER_COMMAND,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        server_ready = wait_for_output(
            server_proc, "🌐 WebSocketIO: Listening on", timeout=10
        )
        assert server_ready, "Server did not start listening on WebSocket."

        # Start the client
        client_proc = subprocess.Popen(
            CLIENT_COMMAND,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        try:
            client_ready = wait_for_output(
                client_proc, "✅ Connected to server", timeout=10
            )
            assert client_ready, "Client did not connect to the server."

        finally:
            client_proc.terminate()
            client_proc.wait(timeout=5)
            if client_proc.stdout:
                client_proc.stdout.close()

    finally:
        server_proc.terminate()
        server_proc.wait(timeout=5)
        if server_proc.stdout:
            server_proc.stdout.close()


def wait_for_output(process, match, timeout=20):
    """Wait for a line in process stdout containing `match`."""
    waited = 0
    poll_interval = 0.1

    while waited < timeout:
        ready, _, _ = select.select([process.stdout], [], [], poll_interval)
        if ready:
            line = process.stdout.readline()
            print("line: " + line.strip())
            if line:
                if match in line:
                    return True
        waited += poll_interval

    return False

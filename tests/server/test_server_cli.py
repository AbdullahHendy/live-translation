import subprocess
import psutil
import select

CLI_COMMAND = ["python", "-u", "-m", "live_translation.server.cli"]


def test_cli_help():
    """Test if `live_translation.cli` runs with --help."""
    result = subprocess.run(CLI_COMMAND + ["--help"], capture_output=True, text=True)

    assert result.returncode == 0, "CLI command failed."
    assert "usage:" in result.stdout.lower(), "CLI command help not found."


def test_cli_invalid_argument():
    """Test invalid CLI argument handling."""
    result = subprocess.run(CLI_COMMAND + ["--invalid"], capture_output=True, text=True)

    assert result.returncode != 0, "CLI command should fail."
    assert "unrecognized arguments" in result.stderr.lower(), (
        "Invalid argument error not found."
    )


def test_cli_real_execution():
    """Test CLI execution."""
    process = subprocess.Popen(
        CLI_COMMAND,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Combine stderr for full output
        text=True,
        bufsize=1,
    )

    timeout = 20
    poll_interval = 0.1
    waited = 0
    found = False

    try:
        while not found and waited < timeout:
            ready, _, _ = select.select([process.stdout], [], [], poll_interval)
            if ready:
                line = process.stdout.readline()
                if line:
                    if "🚀 Starting the pipeline..." in line:
                        found = True
                        break
            waited += poll_interval

        assert found, "CLI didn't start properly"

    finally:
        try:
            parent = psutil.Process(process.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            process.terminate()
            process.wait(timeout=5)
        except Exception as e:
            print(f"⚠️ Process cleanup failed: {e}")

        if process.stdout:
            process.stdout.close()

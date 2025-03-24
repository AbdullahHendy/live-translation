import subprocess
import time
import psutil
import os
import pytest

# If running in GitHub Actions (CI) (skip tests requiring audio hardware)
IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"

EXPECTED_LOGS = [
    "🚀 Starting the pipeline...",
    "🔄 Transcriber: Loading Whisper model...",
    "🔄 Translator: Loading Helsinki-NLP/opus-mt-en-es model...",
    "🎤 Recorder: Listening...",
    "🔄 AudioProcessor: Ready to process audio...",
    "📝 Transcriber: Ready to transcribe audio...",
    "🌍 Translator: Ready to translate text...",
]


@pytest.mark.skipif(
    IN_GITHUB_ACTIONS, reason="Audio hardware not available in GitHub Actions."
)
def test_pipeline():
    """Run PipelineManager with a Config instance then capture logs."""

    process = subprocess.Popen(
        [
            "python",
            "-u",
            "-c",
            "from live_translation._pipeline import PipelineManager; "
            "from live_translation.config import Config; "
            "PipelineManager(Config()).run()",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered to capture logs
    )

    time.sleep(10)

    parent = psutil.Process(process.pid)
    for child in parent.children(recursive=True):
        child.terminate()

    process.terminate()
    process.wait(timeout=5)

    stdout, _ = process.communicate()

    # Check if all expected logs are present
    for log in EXPECTED_LOGS:
        assert log in stdout, f"Missing log: {log}"

    assert process.returncode is not None

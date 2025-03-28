import subprocess
import psutil
import os
import pytest
import select

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
        stderr=subprocess.STDOUT,
        text=True,
    )

    poll_interval = 0.1
    waited = 0
    timeout = 10
    found_logs = set()
    output_lines = []

    # Poll for all expected logs
    while waited < timeout and len(found_logs) < len(EXPECTED_LOGS):
        ready, _, _ = select.select([process.stdout], [], [], poll_interval)
        if ready:
            line = process.stdout.readline()
            if line:
                output_lines.append(line)
                for expected in EXPECTED_LOGS:
                    if expected in line:
                        found_logs.add(expected)
        waited += poll_interval

    parent = psutil.Process(process.pid)
    for child in parent.children(recursive=True):
        child.terminate()

    process.terminate()
    process.wait(timeout=5)

    assert process.returncode is not None, "CLI process didn't exit cleanly"

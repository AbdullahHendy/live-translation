import subprocess
import psutil
import select

EXPECTED_LOGS = [
    "🚀 Starting the pipeline...",
    "🔄 Transcriber: Loading Whisper model...",
    "🔄 Translator: Loading Helsinki-NLP/opus-mt-en-es model...",
    "🔄 AudioProcessor: Ready to process audio...",
    "📝 Transcriber: Ready to transcribe audio...",
    "🌍 Translator: Ready to translate text...",
]


def test_pipeline():
    """Run PipelineManager with a Config instance then capture logs."""

    process = subprocess.Popen(
        [
            "python",
            "-u",
            "-c",
            "from live_translation.server._pipeline import PipelineManager; "
            "from live_translation.server.config import Config; "
            "PipelineManager(Config()).run()",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    poll_interval = 0.1
    waited = 0
    timeout = 20
    found_logs = set()

    # Poll for all expected logs
    while waited < timeout and len(found_logs) < len(EXPECTED_LOGS):
        ready, _, _ = select.select([process.stdout], [], [], poll_interval)
        if ready:
            line = process.stdout.readline()
            if line:
                for expected in EXPECTED_LOGS:
                    if expected in line:
                        found_logs.add(expected)
                    
                if len(found_logs) == len(EXPECTED_LOGS):
                    break
                    
        waited += poll_interval

    parent = psutil.Process(process.pid)
    for child in parent.children(recursive=True):
        child.terminate()

    process.terminate()
    process.wait(timeout=5)

    # Assert that all expected logs were found
    missing_logs = [log for log in EXPECTED_LOGS if log not in found_logs]
    assert not missing_logs, f"Missing expected logs: {missing_logs}"

    assert process.returncode is not None, "CLI process didn't exit cleanly"

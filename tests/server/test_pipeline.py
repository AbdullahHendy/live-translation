import os
from unittest.mock import patch, MagicMock
from live_translation.server._pipeline import PipelineManager
from live_translation.server.config import Config


def test_pipeline_starts_correct_components_translate():
    cfg = Config()

    fake_ws = MagicMock()
    fake_ap = MagicMock()
    fake_tr = MagicMock()
    fake_tx = MagicMock()

    with (
        patch("live_translation.server._pipeline.WebSocketIO", return_value=fake_ws),
        patch("live_translation.server._pipeline.AudioProcessor", return_value=fake_ap),
        patch("live_translation.server._pipeline.Transcriber", return_value=fake_tr),
        patch("live_translation.server._pipeline.Translator", return_value=fake_tx),
    ):
        pipeline = PipelineManager(cfg)
        pipeline.run_async()

        # Assert all components were started
        fake_ws.start.assert_called_once()
        fake_ap.start.assert_called_once()
        fake_tr.start.assert_called_once()
        fake_tx.start.assert_called_once()


def test_pipeline_starts_correct_components():
    cfg = Config(transcribe_only=True)

    fake_ws = MagicMock()
    fake_ap = MagicMock()
    fake_tr = MagicMock()
    fake_tx = MagicMock()

    with (
        patch("live_translation.server._pipeline.WebSocketIO", return_value=fake_ws),
        patch("live_translation.server._pipeline.AudioProcessor", return_value=fake_ap),
        patch("live_translation.server._pipeline.Transcriber", return_value=fake_tr),
        patch("live_translation.server._pipeline.Translator", return_value=fake_tx),
    ):
        pipeline = PipelineManager(cfg)
        pipeline.run_async()

        # Assert all components were started except translator
        fake_ws.start.assert_called_once()
        fake_ap.start.assert_called_once()
        fake_tr.start.assert_called_once()
        fake_tx.start.assert_not_called()


def test_pipeline_stops_components():
    cfg = Config(transcribe_only=True)  # skip translator to simplify

    fake_ws = MagicMock()
    fake_ap = MagicMock()
    fake_tr = MagicMock()

    with (
        patch("live_translation.server._pipeline.WebSocketIO", return_value=fake_ws),
        patch("live_translation.server._pipeline.AudioProcessor", return_value=fake_ap),
        patch("live_translation.server._pipeline.Transcriber", return_value=fake_tr),
    ):
        pipeline = PipelineManager(cfg)
        pipeline.run_async()

        pipeline.stop()

        # These should be joined/stopped
        fake_ws.join.assert_called()
        fake_ap.join.assert_called()
        fake_tr.join.assert_called()


def test_signal_handler_parent_sets_stop_event():
    cfg = Config()
    pipeline = PipelineManager(cfg)

    # Confirm test is running in parent process
    assert os.getpid() == pipeline._parent_pid

    pipeline._stop_event = MagicMock()

    pipeline.signal_handler(sig=2, frame=None)  # SIGINT

    pipeline._stop_event.set.assert_called_once()


def test_signal_handler_ignored_in_child():
    cfg = Config()
    pipeline = PipelineManager(cfg)

    # Fake being in a child process. Ignored in signal_handler()
    with patch("os.getpid", return_value=pipeline._parent_pid + 1):
        pipeline._stop_event = MagicMock()
        pipeline.signal_handler(sig=2, frame=None)

        pipeline._stop_event.set.assert_not_called()

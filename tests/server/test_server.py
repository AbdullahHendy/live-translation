from unittest import mock
from live_translation.server.server import LiveTranslationServer
from live_translation.server.config import Config


def test_server_initialization():
    cfg = Config(device="cpu")
    server = LiveTranslationServer(cfg)
    assert isinstance(server.pipeline_manager, object)


@mock.patch("torch.cuda.is_available", return_value=True)
@mock.patch("multiprocessing.set_start_method")
@mock.patch("live_translation.server.server.PipelineManager")
def test_server_set_spawn_on_cuda(
    MockPipelineManager, mock_set_start_method, mock_cuda_available
):
    cfg = Config(device="cuda")

    server = LiveTranslationServer(cfg)

    mock_set_start_method.assert_called_once_with("spawn", force=True)
    assert isinstance(server, LiveTranslationServer)


@mock.patch("live_translation.server.server.PipelineManager")
def test_server_run_blocking(MockPipelineManager):
    cfg = Config()
    server = LiveTranslationServer(cfg)

    server.run(blocking=True)

    MockPipelineManager.return_value.run.assert_called_once()


@mock.patch("live_translation.server.server.PipelineManager")
def test_server_run_non_blocking(MockPipelineManager):
    cfg = Config()
    server = LiveTranslationServer(cfg)

    server.run(blocking=False)

    MockPipelineManager.return_value.run_async.assert_called_once()


@mock.patch("live_translation.server.server.PipelineManager")
def test_server_stop(MockPipelineManager):
    cfg = Config()
    server = LiveTranslationServer(cfg)

    server.stop()

    MockPipelineManager.return_value.stop.assert_called_once()

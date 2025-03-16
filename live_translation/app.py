# live_translation.py

from config import Config
import multiprocessing as mp
from _pipeline import PipelineManager


class LiveTranslationApp:
    """Encapsulates the Live Translation App Pipeline."""

    def __init__(self, cfg: Config):
        """Initializes the Live Translation App with a Config object."""
        self.cfg = cfg

        # Force spawn insted of fork to accommodate Cuda reinitialization in 
        # forked processes on OS with default forking paradigm (linux, MacOS). 
        # See: 
        # https://huggingface.co/docs/datasets/main/en/process#multiprocessing
        if cfg.DEVICE == "cuda":
            mp.set_start_method("spawn", force=True)

        self.pipeline_manager = PipelineManager(self.cfg)

    def run(self):
        """Starts the translation pipeline."""
        print(f"🚀 Starting live-translation with config: {self.cfg.__dict__}")
        self.pipeline_manager.run()

    # Might be useless in this app's context, but maybe a good to have
    def stop(self):
        """Stops the translation pipeline gracefully."""
        print("🛑 Stopping live-translation...")
        self.pipeline_manager.stop_pipeline()

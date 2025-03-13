import config
import multiprocessing as mp
from args import get_args
from pipeline_manager import PipelineManager


def main():
    # Get configuration settings from command-line arguments
    cfg = config.Config(get_args())
    
    # Force spawn insted of fork to accommodate Cuda reinitialization in forked
    # processes on OS with default forking paradigm (linux, MacOS). 
    # See: https://huggingface.co/docs/datasets/main/en/process#multiprocessing
    if cfg.DEVICE == "cuda":
        mp.set_start_method("spawn", force=True)

    print(f"🚀 Starting live-translation with config: {cfg.__dict__}")

    # Create and run the pipeline manager
    pipeline_manager = PipelineManager(cfg)
    pipeline_manager.run()

if __name__ == "__main__":
    main()

import config
from args import get_args
from pipeline_manager import PipelineManager


def main():
    # Get configuration settings from command-line arguments
    cfg = config.Config(get_args())
    
    print(f"🚀 Starting live-translation with config: {cfg.__dict__}")

    # Create and run the pipeline manager
    pipeline_manager = PipelineManager(cfg)
    pipeline_manager.run()

if __name__ == "__main__":
    main()

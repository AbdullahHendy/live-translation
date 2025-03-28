import multiprocessing as mp


def pytest_configure():
    try:
        mp.set_start_method("spawn")
    except RuntimeError:
        pass  # Already set, ignore

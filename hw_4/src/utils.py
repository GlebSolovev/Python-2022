import time
from typing import Callable, NoReturn


def measure(callable_task: Callable[[], NoReturn], measure_name: str) -> str:
    start = time.time()
    callable_task()
    end = time.time()
    return f"{measure_name}: {end - start:.4f}s"
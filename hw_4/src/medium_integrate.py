import math
import os
import sys
import threading
import time
from concurrent.futures import Executor, ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, Tuple
from typing.io import TextIO

from hw_4.src.easy_fibs import measure


def integrate_task(f: Callable[[float], float], a: float, step: float, iteration: int, start_time: float) \
        -> Tuple[float, str]:
    logs = f"Start iteration: {iteration} at {time.time() - start_time:.4f}s" + \
           f" by thread {threading.get_ident()} of process {os.getpid()}"
    res = f(a + iteration * step) * step
    logs += f"\nFinish iteration: {iteration} at {time.time() - start_time:.4f}s"
    return res, logs


def integrate(f: Callable[[float], float], a: float, b: float, get_pool_executor: Callable[[int], Executor],
              n_jobs: int = 1, n_iter: int = 1000, logs_file: TextIO = sys.stdout, chunk_size: int = 1):
    step = (b - a) / n_iter
    global_start_time = time.time()

    with get_pool_executor(n_jobs) as executor:
        args = [(f, a, step, i, global_start_time) for i in range(n_iter)]
        iterations_res = executor.map(integrate_task, *list(zip(*args)), chunksize=chunk_size)

    values, logs = zip(*iterations_res)
    print("\n".join(logs), file=logs_file)
    return sum(values)


def measure_pools(n_jobs: int, logs_dir: str) -> str:
    pools_info = [
        (lambda max_workers: ThreadPoolExecutor(max_workers=n_jobs), 1,
         f"thread pool with {n_jobs} workers",
         f"thread-pool-{n_jobs}"),
        (lambda max_workers: ProcessPoolExecutor(max_workers=n_jobs), 1,
         f"process pool with {n_jobs} workers and chunk_size 1",
         f"process-pool-{n_jobs}-1"),
        (lambda max_workers: ProcessPoolExecutor(max_workers=n_jobs), 10,
         f"process pool with {n_jobs} workers and chunk_size 10",
         f"process-pool-{n_jobs}-10"),
        (lambda max_workers: ProcessPoolExecutor(max_workers=n_jobs), 100,
         f"process pool with {n_jobs} workers and chunk_size 100",
         f"process-pool-{n_jobs}-100")
    ]

    pools_results = []
    for pool, chunk_size, description, log_filename in pools_info:
        with open(logs_dir + log_filename, "w") as logs_file:
            print(description, file=logs_file)
            pools_results.append(
                measure(lambda: integrate(math.cos, 0, math.pi / 2, pool, n_jobs=n_jobs, logs_file=logs_file,
                                          chunk_size=chunk_size),
                        description))
            print("\n", file=logs_file)

    return "\n".join(pools_results)


if __name__ == '__main__':
    output_directory = "../artifacts/medium/"
    os.makedirs(os.path.dirname(output_directory), exist_ok=True)

    logs_directory = output_directory + "logs/"
    os.makedirs(os.path.dirname(logs_directory), exist_ok=True)

    measurements = "\n\n".join([measure_pools(n_jobs, logs_directory) for n_jobs in range(1, os.cpu_count() * 2 + 1)])

    measurements_filename = output_directory + "measurements.txt"
    with open(measurements_filename, "w") as file:
        file.write(measurements)

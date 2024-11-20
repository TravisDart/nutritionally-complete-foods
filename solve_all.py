"""
This program tries to find all combinations of foods that will meet the nutritional requirements of a person.
See README.md for a full description. In short, the ultimate goal of this project is to find all solutions.
However, it looks like we need a different solver to do this.
"""
import multiprocessing
import time
from typing import List

import psutil

from constants import DB_URL
from solve import solve_it
from solver.initialize import initialize
from solver.logger import Logger
from solver.sql import SQLStore


def solve_job(num_foods, exclusion: List[int], DB_URL):
    foods, max_foods, min_requirements, max_requirements, verbose = initialize()
    foods_without = [food for food in foods if food[0] not in exclusion]
    solution = solve_it(
        foods_without,
        max_foods,
        min_requirements,
        max_requirements,
        num_foods,
        verbose,
    )
    state_store = SQLStore(db_url=DB_URL, num_foods=num_foods)
    state_store.add_result(exclusion, timeout=False, solution=solution)


def solve(process_id: int = 0):
    timeout = 3600
    num_foods = 7
    logger = Logger(verbose=True, process_id=process_id)
    state_store = SQLStore(
        db_url=DB_URL, num_foods=num_foods, logger=logger, timeout=timeout
    )

    state_store.initialize()
    # state_store.resume(clear_timeout=True)

    logical_cores = psutil.cpu_count(logical=True)
    processes = {id: None for id in range(logical_cores)}

    has_more_work = True
    while has_more_work:
        timed_out_processes = state_store.get_timed_out_processes()
        for worker_id in timed_out_processes:
            process, exclusion = processes[worker_id]
            state_store.add_result(exclusion, timeout=True)
            process.terminate()
            processes[worker_id] = None

        for worker_id in processes:
            process = processes[worker_id]
            if process is not None and not process[0].is_alive():
                processes[worker_id] = None

        available_workers = [id for id, process in processes.items() if process is None]
        for worker_id in available_workers:
            exclusion = state_store.get_exclusion(worker_id)
            if exclusion is None:
                # If no workers are working and there are no more exclusions to try, we're done.
                if list(processes.values()).count(None) == logical_cores:
                    has_more_work = False

                # If no exclusions are available, don't try to start new workers.
                break

            process = multiprocessing.Process(
                target=solve_job, args=(num_foods, exclusion, DB_URL)
            )
            process.start()
            processes[worker_id] = (process, exclusion)

        time.sleep(1)


if __name__ == "__main__":
    solve()

"""
This program tries to find all combinations of foods that will meet the nutritional requirements of a person.
See README.md for a full description. In short, the ultimate goal of this project is to find all solutions.
However, it looks like we need a different solver to do this.
"""
import multiprocessing
from itertools import combinations
import functools

import psutil

from constants import DB_FILE_NAME
from solve import solve_it
from solver.initialize import initialize
from solver.logger import Logger, FileLogger

# from solver.local_store import LocalStore
from solver.sql import SQLStore


def solve_it_partial(
    max_foods, min_requirements, max_requirements, num_foods, verbose, foods
):
    return solve_it(
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        num_foods,
        log_level=verbose,
    )


def solve_job(process_id: int = 0, seed_run: bool = False):
    # Initialize the solver function
    # state_store = LocalStore(testing=True)
    num_foods = 7
    logger = Logger(verbose=True, process_id=process_id)
    state_store = SQLStore(DB_FILE_NAME, num_foods, start_over=seed_run, logger=logger)
    foods, max_foods, min_requirements, max_requirements, verbose = initialize()
    solve = functools.partial(
        solve_it_partial,
        max_foods,
        min_requirements,
        max_requirements,
        num_foods,
        verbose,
    )

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Loop until we've tried to solve without the combinations of elements of every solution.

    for exclusion in state_store.exclusions():
        foods_without = [food for food in foods if str(food[0]) not in exclusion]
        try:
            solution = solve(foods_without)
        except KeyboardInterrupt:
            print("!!! Keyboard interrupt !!!")
            exit()
        state_store.add_try(exclusion)
        if solution:
            state_store.add_solution(solution)
            if seed_run:
                break


if __name__ == "__main__":
    # solve_job(seed_run=True)

    logical_cores = 4  # psutil.cpu_count(logical=True)
    print(f"Logical cores: {logical_cores}")
    with multiprocessing.Pool(logical_cores) as p:
        p.map(solve_job, range(1, logical_cores + 1))
        # [
        #     p.apply_async(solve_job, args=(process_id,))
        #     for process_id in range(1, logical_cores + 1)
        # ]
        p.close()

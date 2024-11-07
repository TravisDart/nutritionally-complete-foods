"""
This program tries to find all combinations of foods that will meet the nutritional requirements of a person.
See README.md for a full description. In short, the ultimate goal of this project is to find all solutions.
However, it looks like we need a different solver to do this.
"""
import multiprocessing
from multiprocessing import Lock
import functools
import psutil

from constants import DB_URL
from solve import solve_it
from solver.initialize import initialize
from solver.logger import Logger, FileLogger

# from solver.local_store import LocalStore
from solver.sql import SQLStore


def solve_job(process_id: int = 0):
    # Initialize the solver function
    num_foods = 7
    logger = Logger(verbose=True, process_id=process_id)
    state_store = SQLStore(db_url=DB_URL, num_foods=num_foods, logger=logger)
    foods, max_foods, min_requirements, max_requirements, verbose = initialize()

    # Loop until we've tried to solve without the combinations of elements of every solution.
    for exclusion in state_store.exclusions():
        foods_without = [food for food in foods if food[0] not in exclusion]
        try:
            solution = solve_it(
                foods_without,
                max_foods,
                min_requirements,
                max_requirements,
                num_foods,
                verbose,
            )
        except KeyboardInterrupt:
            print("!!! Keyboard interrupt !!!")
            exit()
        state_store.add_try(exclusion)
        if solution:
            state_store.add_solution(solution)
        else:
            logger.log("No solution for exclusion", exclusion)


if __name__ == "__main__":
    num_foods = 7
    SQLStore.initialize(DB_URL)
    # solve_job(1)  # For debugging
    # exit()

    logical_cores = psutil.cpu_count(logical=True)
    print(f"Logical cores: {logical_cores}")
    with multiprocessing.Pool(logical_cores) as p:
        p.map(solve_job, range(1, logical_cores + 1))
        p.close()

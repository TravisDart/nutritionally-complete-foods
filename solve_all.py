"""
This program tries to find all combinations of foods that will meet the nutritional requirements of a person.
See README.md for a full description. In short, the ultimate goal of this project is to find all solutions.
However, it looks like we need a different solver to do this.
"""
import multiprocessing
from multiprocessing import Lock
import functools
import psutil

from constants import SOLUTION_FILE_NAME, TRIED_FILE_NAME
from solve import solve_it
from solver.initialize import initialize
from solver.logger import Logger, FileLogger

# from solver.local_store import LocalStore
from solver.file_store import FileStore


def solve_job(process_id: int = 0):
    def get_global(lock):
        try:
            return globals()[lock]
        except KeyError:
            return None

    solution_lock = get_global("solution_lock")
    tried_lock = get_global("tried_lock")

    print("solution_lock, tried_lock", solution_lock, tried_lock)
    # Initialize the solver function
    # state_store = LocalStore(testing=True)
    num_foods = 7
    logger = Logger(verbose=True, process_id=process_id)
    state_store = FileStore(
        solution_file_name=SOLUTION_FILE_NAME,
        tried_file_name=TRIED_FILE_NAME,
        solution_lock=solution_lock,
        tried_lock=tried_lock,
        num_foods=num_foods,
        logger=logger,
    )
    foods, max_foods, min_requirements, max_requirements, verbose = initialize()
    solve = functools.partial(
        # Reorder the arguments to put foods last.
        lambda max_foods, min_requirements, max_requirements, num_foods, verbose, foods: solve_it(
            foods,
            max_foods,
            min_requirements,
            max_requirements,
            num_foods,
            log_level=verbose,
        ),
        max_foods,
        min_requirements,
        max_requirements,
        num_foods,
        verbose,
    )

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Loop until we've tried to solve without the combinations of elements of every solution.

    while exclusion := state_store.exclusions():
        print("exclusion", exclusion)
        foods_without = [food for food in foods if str(food[0]) not in exclusion]
        try:
            solution = solve(foods_without)
        except KeyboardInterrupt:
            print("!!! Keyboard interrupt !!!")
            exit()
        state_store.add_try(exclusion)
        if solution:
            state_store.add_solution(solution)


def init_pool_processes(solution_lock_arg, tried_lock_arg):
    """Initialize each process with a global variable lock."""
    global solution_lock
    solution_lock = solution_lock_arg
    global tried_lock
    tried_lock = tried_lock_arg


def first_run(num_foods):
    foods, max_foods, min_requirements, max_requirements, verbose = initialize()
    solution = solve_it(
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        num_foods,
        log_level=verbose,
    )
    # Truncate the state files and write the solution to the solution file.
    FileStore.initialize(solution, SOLUTION_FILE_NAME, TRIED_FILE_NAME)


if __name__ == "__main__":
    num_foods = 7
    first_run(num_foods)

    logical_cores = 4  # psutil.cpu_count(logical=True)
    print(f"Logical cores: {logical_cores}")
    solution_lock = Lock()
    tried_lock = Lock()
    with multiprocessing.Pool(
        logical_cores,
        initializer=init_pool_processes,
        initargs=(solution_lock, tried_lock),
    ) as p:
        p.map(solve_job, range(1, logical_cores + 1))
        p.close()

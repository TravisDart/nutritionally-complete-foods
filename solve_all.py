"""
This program tries to find all combinations of foods that will meet the nutritional requirements of a person.
See README.md for a full description. In short, the ultimate goal of this project is to find all solutions.
However, it looks like we need a different solver to do this.
"""
import multiprocessing
from itertools import combinations
import functools

from constants import DB_FILE_NAME
from solve import solve_it
from solver import sql
from solver.initialize import initialize
from solver.local_store import LocalStore
from solver.sql import SQLStore


def solve_it2(max_foods, min_requirements, max_requirements, num_foods, verbose, foods):
    return solve_it(
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        num_foods,
        log_level=verbose,
    )


def solve_job():
    # Initialize the solver function
    # state_store = LocalStore(testing=True)
    num_foods = 7
    state_store = SQLStore(DB_FILE_NAME, num_foods, start_over=True, verbose=True)
    foods, max_foods, min_requirements, max_requirements, verbose = initialize()
    solve = functools.partial(
        solve_it2,
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
        solution = solve(foods_without)
        state_store.add_try(exclusion)
        if solution:
            state_store.add_solution(solution)


if __name__ == "__main__":
    solve_job()

from itertools import combinations
from multiprocessing import Pool

import numpy as np
import psutil
from scipy.optimize import linprog

from constants import DB_URL, FOOD_OFFSET, TOP_FOODS
from solver.initialize import initialize
from solver.logger import Logger
from solver.simple_sql import SimpleSQLStore


def solution_exists(A, B, C):
    """
    Check if there exists a solution to the linear programming problem A <= Bx <= C

    :param A: Lower bound
    :param B: Matrix of coefficients
    :param C: Upper bound
    :return: Boolean indicating if a solution exists
    """
    result = linprog(
        # The objective function (any objective function will do, we just care that the inequality holds)
        c=np.ones(B.shape[1]),
        # Define the equality constraints (Bx - s1 = A and Bx + s2 = C)
        A_ub=np.vstack((B, -B)),
        b_ub=np.hstack((C, -A)),
        method="highs",
    )

    return result.success


def iterate_over_combos(food_ids, num_foods, worker_id, total_workers):
    loop_counter = 0
    for y in combinations(food_ids, num_foods):
        loop_counter += 1
        if loop_counter % total_workers == worker_id:
            yield y


def find_all(
    worker_id: int,
    total_workers: int,
    food_ids,
    foods,
    min_requirements,
    max_requirements,
    num_foods,
):
    logger = Logger(verbose=True, process_id=worker_id)
    state_store = SimpleSQLStore(db_url=DB_URL, num_foods=num_foods, logger=logger)
    state_store.initialize()

    worker_loop_counter = 0
    for combination in iterate_over_combos(
        food_ids, num_foods, worker_id, total_workers
    ):
        worker_loop_counter += 1
        if worker_loop_counter % 10000 == 0:
            state_store.add_work(worker_id, worker_loop_counter)
        combo_list = [foods[i] for i in combination]
        good_solution = solution_exists(
            A=min_requirements,
            B=np.transpose(np.array(combo_list)),
            C=max_requirements,
        )
        if good_solution:
            state_store.add_solution(combination)


def known_good_solution():
    food_ids = [
        2020,
        2047,
        4516,
        4572,
        11110,
        11506,
        11525,
        11936,
        11946,
        11998,
        14353,
        35093,
        43365,
        48052,
    ]

    (
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        verbose,
        _,  # num_foods (not applicable for this solver)
    ) = initialize(only_these_ids=food_ids, verbose=False)

    foods = [f[FOOD_OFFSET:] for f in foods]

    min_requirements = np.array(min_requirements)
    max_requirements = np.array(max_requirements)

    good_solution = solution_exists(
        A=min_requirements,
        B=np.transpose(np.array(foods)),
        C=max_requirements,
    )
    print("good_solution?", good_solution)
    return good_solution


def known_bad_solution():
    is_good = solution_exists(
        A=np.array([1, 1, 1]),
        B=np.transpose(np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])),
        C=np.array([10, 10, 10]),
    )
    print("good_solution?", is_good)
    return is_good


def trivial_good_solution():
    is_good = solution_exists(
        A=np.array([1, 1, 1]),
        B=np.transpose(np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])),
        C=np.array([10, 10, 10]),
    )
    print("good_solution?", is_good)
    return is_good


def find_all_solutions():
    num_foods = 4

    (
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        verbose,
        _,  # num_foods (not applicable for this solver)
    ) = initialize(only_these_ids=TOP_FOODS, verbose=False)

    min_requirements = np.array(min_requirements)
    max_requirements = np.array(max_requirements)

    foods = {  # Map Food ID to the food's nutrient values
        f[0]: f[FOOD_OFFSET:] for f in foods
    }

    logical_cores = psutil.cpu_count(logical=True)

    with Pool(processes=logical_cores) as pool:
        args = [
            (
                worker_id,
                logical_cores,
                TOP_FOODS,
                foods,
                min_requirements,
                max_requirements,
                num_foods,
            )
            for worker_id in range(0, logical_cores)
        ]
        pool.starmap(find_all, args)


if __name__ == "__main__":
    # known_good_solution()
    # known_bad_solution()
    # trivial_good_solution()
    find_all_solutions()

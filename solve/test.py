import time

import numpy as np

from constants import KNOWN_SOLUTIONS, FOOD_OFFSET
from find_max import find_food_max_value
from find_n_greatest import find_max_error
from download_data import load_test_data, load_data
from solve import solve_it
from utils import (
    ordered_dict_values,
    dict_to_ordered_tuples,
    verify_solution,
    evaluate_result,
)


def trivial_tests(verbose=False):
    for food_set in [2]:  # range(3):
        (
            foods,
            min_requirements,
            max_requirements,
            expected_max_foods,
            expected_max_error,
        ) = load_test_data(food_set)

        max_foods = find_food_max_value(foods, max_requirements)
        assert max_foods == expected_max_foods

        fme = find_max_error(foods, max_foods, len(foods), min_requirements)
        assert fme == expected_max_error

        solver_result = solve_it(
            foods,
            max_foods,
            min_requirements,
            max_requirements,
            num_foods=len(foods),
            log_level=int(verbose),
        )

        just_matrix_coefficients = [[y for y in x[FOOD_OFFSET:]] for x in foods]
        A = np.array(just_matrix_coefficients)
        A = A.T

        food_quantity = list(solver_result.values())[0]["food_quantity"]
        solution = ordered_dict_values(food_quantity)

        result = A @ solution
        evaluate_result(
            result,
            min_requirements,
            max_requirements,
            verbose=verbose,
            should_assert=True,
        )
        if verbose:
            print(f"Test {food_set} passed")


def multiply_known_solutions(verbose=False, should_assert=True):
    """Multiply out each known solution to see if it's really a solution."""
    for number_of_foods in KNOWN_SOLUTIONS:
        for known_solution in KNOWN_SOLUTIONS[number_of_foods]:
            verify_solution(
                known_solution, verbose=verbose, should_assert=should_assert
            )


def solve_against_known_solutions(verbose=False):
    """Run the solver against just the foods in the known solutions to verify that a solution can be found."""
    for number_of_foods in KNOWN_SOLUTIONS:
        for known_solution in KNOWN_SOLUTIONS[number_of_foods]:
            # Make sure the solution is sorted by ID.
            known_solution = sorted(known_solution, key=lambda x: x[0])

            ids = [x[0] for x in known_solution]
            (
                foods_in_solution,
                max_foods,
                min_requirements,
                max_requirements,
            ) = load_data(only_these_ids=ids)

            solver_result = solve_it(
                foods_in_solution,
                max_foods,
                min_requirements,
                max_requirements,
                num_foods=len(known_solution),
                log_level=int(verbose) * 2,
            )
            assert len(solver_result) == 1  # Only one solution

            # Convert the dict-formatted solution to a tuple format. We need to make this more consistent.
            food_quantity = list(solver_result.values())[0]["food_quantity"]
            tuple_solution = dict_to_ordered_tuples(food_quantity)

            verify_solution(tuple_solution, verbose=verbose)


def time_it(func, *args, **kwargs):
    start_time = time.time()
    func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    print("Known solutions took", execution_time, "seconds to solve.")


if __name__ == "__main__":
    trivial_tests(verbose=False)
    multiply_known_solutions(verbose=False, should_assert=True)
    time_it(solve_against_known_solutions, verbose=False)
    print("All assertions pass.")

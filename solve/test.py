"""
This is currently unused. The goal of this program was so the solution didn't have to provide a quantity for each food.
Instead, we could just save the food IDs and use this program to recalculate the coefficients as needed.

# How this program works:

Find a solution x to the matrix equation c < A*x such that the value is as close to c as possible.
The matrix A can be non-square, but has the same number of rows as c has elements.

I thought at first, this would return the same result as the solver in the same circumstances,
but, for example, if we have:

A = [
  [0 0 1],
  [1 1 1],
]
c = [1 1 1]

The solver may choose x = [1 1], but this function will choose x = [0 1] 
(I guess it doesn't really matter, though.)

Or, in practical terms, given the food data as a matrix A, and the dietary requirements as a vector c,
solve the vector x to find the quantities of food.
"""

import numpy as np
import time
from load_data import load_requirements, load_subset_of_data, load_test_data
from solve import solve_it
from constants import KNOWN_SOLUTIONS


def ordered_dict_values(food_quantity: dict[str, int]):
    """Turn the dictionary into a list of values, being sure to preserve the id order of the keys."""
    return [x[1] for x in sorted(food_quantity.items(), key=lambda item: int(item[0]))]


def _evaluate_result(solution, min_bound, max_bound, verbose=True, assert_good=False):
    error = np.linalg.norm(solution - min_bound)
    under_bounds = [solution[x] < min_bound[x] for x in range(len(max_bound))]
    under_bounds_str = "".join(["1" if x else "0" for x in under_bounds])
    over_bounds = [solution[x] > max_bound[x] for x in range(len(max_bound))]
    over_bounds_str = "".join(["1" if x else "0" for x in over_bounds])
    is_out_of_bounds = any(under_bounds) or any(over_bounds)

    if verbose:
        print("solution", solution)
        print("error", error)
        print("Components Under Bounds (Bitstring)", under_bounds_str)
        print("Components Over Bounds  (Bitstring)", over_bounds_str)
        print("is_out_of_bounds", is_out_of_bounds)

    if assert_good:
        assert not is_out_of_bounds

    return (
        error,
        under_bounds,
        over_bounds,
        is_out_of_bounds,
        under_bounds_str,
        over_bounds_str,
    )


def multiply_known_solutions():
    """Multiply out each known solution to see if it's really a solution."""

    for number_of_foods in KNOWN_SOLUTIONS:
        for known_solution in KNOWN_SOLUTIONS[number_of_foods]:
            ids = [x[0] for x in known_solution]
            example_foods, _ = load_subset_of_data(ids=ids)
            just_matrix_coefficients = [[y[0] for y in x[4:]] for x in example_foods]
            A = np.array(just_matrix_coefficients)
            A = A.T
            min_requirements, max_requirements, _ = load_requirements()

            solution = [x[1] for x in known_solution]
            result = A @ solution
            _evaluate_result(
                result, min_requirements, max_requirements, assert_good=True
            )


def solve_against_known_solutions(verbose=True):
    """Run the solver against just the foods in the known solutions to verify that a solution can be found."""

    for number_of_foods in KNOWN_SOLUTIONS:
        for known_solution in KNOWN_SOLUTIONS[number_of_foods]:
            ids = [x[0] for x in known_solution]
            example_foods, _ = load_subset_of_data(ids=ids)
            just_matrix_coefficients = [[y[0] for y in x[4:]] for x in example_foods]
            A = np.array(just_matrix_coefficients)
            A = A.T
            min_requirements, max_requirements, _ = load_requirements()

            # Part 2: Solve it with the solver
            solver_result = solve_it(
                min_requirements,
                max_requirements,
                example_foods,
                log_level=int(verbose),
            )
            assert len(solver_result) == 1  # Only one solution

            food_quantity = list(solver_result.values())[0]["food_quantity"]
            solution = ordered_dict_values(food_quantity)

            result = A @ solution
            _evaluate_result(
                result,
                min_requirements,
                max_requirements,
                verbose=verbose,
                assert_good=True,
            )


def trivial_tests(verbose=True):
    for food_set in range(3):
        (
            nutrients,
            example_foods,
            food_labels,
            min_requirements,
            max_requirements,
        ) = load_test_data(food_set)
        del food_labels

        solver_result = solve_it(
            min_requirements,
            max_requirements,
            example_foods,
            num_foods=len(example_foods),
            log_level=int(verbose),
        )

        just_matrix_coefficients = [[y[0] for y in x[4:]] for x in example_foods]
        A = np.array(just_matrix_coefficients)
        A = A.T

        food_quantity = list(solver_result.values())[0]["food_quantity"]
        solution = ordered_dict_values(food_quantity)

        result = A @ solution
        _evaluate_result(
            result,
            min_requirements,
            max_requirements,
            verbose=verbose,
            assert_good=True,
        )
        if verbose:
            print(f"Test {food_set} passed")


def benchmark_solving():
    print("Benchmarking solver speed")
    # About 100 solutions per second
    t = time.process_time()
    iterations = 100
    for x in range(iterations):
        solve_against_known_solutions(verbose=False)
        trivial_tests(verbose=False)
    elapsed_time = time.process_time() - t
    print(
        "elapsed_time",
        elapsed_time,
        "solutions/sec:",
        iterations * (len(KNOWN_SOLUTIONS) + 3) / elapsed_time,
    )


if __name__ == "__main__":
    # trivial_tests()
    # multiply_known_solutions()
    solve_against_known_solutions()
    print("All assertions pass.")

    # benchmark_solving()

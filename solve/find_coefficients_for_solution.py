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
from scipy.optimize import minimize
import time
from load_data import load_requirements, load_subset_of_data, load_test_data
from solve import solve_it
from constants import KNOWN_SOLUTIONS


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


def benchmark_solving():
    example_foods = load_subset_of_data(
        ids=[
            14091,
            14355,
            9068,
            11672,
        ]
    )
    just_matrix_coefficients = [[y[0] for y in x[4:]] for x in example_foods]
    A = np.array(just_matrix_coefficients)
    A = A.T
    min_requirements, max_requirements, _ = load_requirements()

    # About 100 solutions per second
    t = time.process_time()
    iterations = 1000
    for x in range(iterations):
        solve_it(min_requirements, max_requirements, example_foods)
    elapsed_time = time.process_time() - t
    print("elapsed_time", elapsed_time, "iter/sec:", iterations / elapsed_time)


def multiply_known_solutions():
    """Multiply out each known solution to see if it's really a solution."""

    for known_solution in KNOWN_SOLUTIONS[4]:
        ids = [x[0] for x in known_solution]
        example_foods, _ = load_subset_of_data(ids=ids)
        just_matrix_coefficients = [[y[0] for y in x[4:]] for x in example_foods]
        A = np.array(just_matrix_coefficients)
        A = A.T
        min_requirements, max_requirements, _ = load_requirements()

        solution = [x[1] for x in known_solution]
        result = A @ solution
        _evaluate_result(result, min_requirements, max_requirements, assert_good=False)


def solve_against_known_solutions():
    """Run the solver against just the foods in the known solutions to verify that a solution can be found."""

    for known_solution in KNOWN_SOLUTIONS[4]:
        ids = [x[0] for x in known_solution]
        example_foods, _ = load_subset_of_data(ids=ids)
        just_matrix_coefficients = [[y[0] for y in x[4:]] for x in example_foods]
        A = np.array(just_matrix_coefficients)
        A = A.T
        min_requirements, max_requirements, _ = load_requirements()

        # Part 2: Solve it with the solver
        solver_result = solve_it(
            min_requirements, max_requirements, example_foods, log_level=1
        )
        assert len(solver_result) == 1  # Only one solution

        food_quantity = list(solver_result.values())[0]["food_quantity"]
        solution = []
        # TODO: There's probably a better order-preserving way to do this.
        for id in ids:
            solution += [food_quantity[str(id)]]

        # # Also works
        # food_quantity = list(solver_result.values())[0]["food_quantity"]
        # sorted_tuples = sorted(food_quantity.items(), key=lambda item: int(item[0]))
        # solution = list([x[1] for x in sorted_tuples])

        result = A @ solution
        _evaluate_result(result, min_requirements, max_requirements)


def tests2():
    nutrients, example_foods, min_requirements, max_requirements = load_test_data()
    solver_result = solve_it(
        min_requirements,
        max_requirements,
        example_foods,
        num_foods=len(example_foods),
        log_level=1,
    )

    just_matrix_coefficients = [[y[0] for y in x[4:]] for x in example_foods]
    A = np.array(just_matrix_coefficients)
    A = A.T

    food_quantity = list(solver_result.values())[0]["food_quantity"]
    solution = []
    # TODO: There's probably a better order-preserving way to do this.
    for id in [1, 2, 3]:
        solution += [food_quantity[str(id)]]

    result = A @ solution
    _evaluate_result(result, min_requirements, max_requirements)
    print("Test2 passed")


def tests():
    # Test 1: A is non-square
    # fmt: off
    A = np.array([
        [1, 0, 0],
        [0, 1, 1]
    ])  # Non-square A
    # fmt: on
    A = A.T
    c = np.array([2, 2, 2])

    x = find_closest_solution(A, c)
    assert np.array_equal(x, [2, 2])
    print("Test1 passed")

    # Test 2: Square A
    # fmt: off
    A = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]) 
    # fmt: on
    A = A.T
    c = np.array([2, 2, 2])

    x = find_closest_solution(A, c)
    assert np.array_equal(x, [2, 2, 2])
    print("Test2 passed")

    # Test 3: Floats
    # fmt: off
    A = np.array([
        [1, .5, 0],
        [0, .5, 1],
    ])
    # fmt: on
    A = A.T
    c = np.array([2, 2, 2])

    x = find_closest_solution(A, c)
    assert np.array_equal(x, [2, 2])
    print("Test3 passed")

    # Test 4: 1-dimensional
    # fmt: off
    A = np.array([
        [1, 1, 1],
    ])
    # fmt: on
    A = A.T
    c = np.array([2, 2, 2])

    x = find_closest_solution(A, c)
    assert np.array_equal(
        x,
        [2, 2],
    )
    print("Test4 passed")


if __name__ == "__main__":
    tests2()
    # multiply_known_solutions()
    # solve_against_known_solutions()

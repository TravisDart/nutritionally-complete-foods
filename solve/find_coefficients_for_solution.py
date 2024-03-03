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


def objective_function(x, A, c):
    """Calculates the squared distance between c and A*x."""
    return np.linalg.norm(A @ x - c) ** 2


def convert_and_find_closest_solution(subset_ids, foods, nutrients, FOOD_OFFSET):
    food_subset = [
        [sublist[0] for sublist in f[FOOD_OFFSET:]] for f in foods if f[0] in subset_ids
    ]
    A = np.array(food_subset)
    A = A.T

    c = np.array([nutrient[1][0] for nutrient in nutrients])

    x = find_closest_solution(A, c)
    return x


def find_closest_solution(A, c):
    """Finds a solution x to the equation c < A*x, minimizing distance to c."""
    minimize_result = minimize(
        objective_function,
        x0=np.zeros(A.shape[1]),
        args=(A, c),
        bounds=[(-np.inf, np.inf) for _ in range(A.shape[1])],
    )
    result = np.round(minimize_result.x)
    return result


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
    tests()

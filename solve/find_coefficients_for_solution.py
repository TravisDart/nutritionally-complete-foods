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
from load_data import load_requirements, load_subset_of_data
from solve import solve_it


def find_closest_solution3(A, c, d):
    # def objective_function(x):
    #     """Objective function to minimize the sum of squared slack variables."""
    #     lower_slack = np.maximum(0, c - A @ x)  # Non-negative slack for lower bound
    #     upper_slack = np.maximum(0, A @ x - d)  # Non-negative slack for upper bound
    #     return np.sum(lower_slack**2 + upper_slack**2)

    def objective_function(x):
        """Objective function to minimize the sum of squared slack variables."""
        slack = np.maximum(0, c - A @ x)  # Non-negative slack variables
        return np.sum(slack**2)

    # Initial guess for x (can be adjusted if needed)
    x0 = np.ones(4)
    # x0 = np.array([1227, 804, 3382, 913])

    # Define constraints to ensure A*x > c element-wise
    constraints = [
        {"type": "ineq", "fun": lambda x: A @ x - c},
        {"type": "ineq", "fun": lambda x: d - A @ x},
    ]

    # TODO: try L-BFGS-B or Nelder-Mead.
    # Minimize the objective function subject to the constraints
    res = minimize(objective_function, x0, method="SLSQP", constraints=constraints)

    # Check if a solution is found and strictly satisfies the constraints
    print("res.success", res.success)
    if res.success:
        print("res.x", res.x)
        solution = res.x
        if np.all(A @ solution > c) and np.all(A @ solution < d):  # Strict satisfaction
            return solution
        else:
            return None  # No solution that strictly satisfies the inequality
    else:
        return None  # Optimization failed to find a solution


def find_closest_solution2(A, c):
    x = np.linalg.lstsq(A, c, rcond=None)
    x = np.ceil(x[0])
    return x


def find_closest_solution(A, c):
    """
    Finds a solution x to the equation c < A*x, minimizing distance to c.

    In our application:
      c is the minimum requirements for each nutrient
      A is the matrix of nutrients in each food
    """

    def objective_function(x, A, c):
        """Calculates the squared distance between c and A*x."""
        return np.linalg.norm(A @ x - c)  # ** 2

    minimize_result = minimize(
        objective_function,
        x0=np.zeros(A.shape[1]),
        args=(A, c),
        bounds=[(0, np.inf) for _ in range(A.shape[1])],
    )
    result = np.ceil(minimize_result.x)
    return result


def evaluate_result(solution, min_bound, max_bound):
    error = np.linalg.norm(solution - min_bound)
    under_bounds = [solution[x] < min_bound[x] for x in range(len(max_bound))]
    under_bounds_str = "".join(["1" if x else "0" for x in under_bounds])
    over_bounds = [solution[x] > max_bound[x] for x in range(len(max_bound))]
    over_bounds_str = "".join(["1" if x else "0" for x in over_bounds])
    is_out_of_bounds = any(under_bounds) or any(over_bounds)

    return (
        error,
        under_bounds,
        over_bounds,
        is_out_of_bounds,
        under_bounds_str,
        over_bounds_str,
    )


def benchmark_solving():
    # TODO: un-duplicate this code
    # # fmt: off
    # example_foods = [
    #     ['14091', 'Beverages', 'Beverages, almond milk, unsweetened, shelf stable', '', (1840, 'mg'), (13, 'g'), (31, 'mg'), (0, 'mg'), (150, 'kcal'), (10, 'g'), (2, 'g'), (0, None), (10, 'µg'), (3, 'mg'), (60, 'mg'), (400, 'µg'), (1, 'mg'), (90, 'mg'), (670, 'mg'), (4, 'g'), (0, 'mg'), (1, 'µg'), (720, 'mg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (10, 'µg'), (63, 'mg'), (0, 'µg'), (965, 'g'), (1, 'mg')],
    #     ['14355', 'Beverages', 'Beverages, tea, black, brewed, prepared with tap water', '', (0, 'mg'), (3, 'g'), (4, 'mg'), (0, 'mg'), (10, 'kcal'), (0, 'g'), (0, 'g'), (3730, 'µg'), (50, 'µg'), (0, 'mg'), (30, 'mg'), (2190, 'µg'), (0, 'mg'), (10, 'mg'), (370, 'mg'), (0, 'g'), (0, 'mg'), (0, 'µg'), (30, 'mg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (997, 'g'), (0, 'mg')],
    #     ['9024', 'Fruits and Fruit Juices', 'Apricots, canned, juice pack, with skin, solids and liquids', '', (120, 'mg'), (123, 'g'), (18, 'mg'), (1, 'mg'), (480, 'kcal'), (0, 'g'), (16, 'g'), (0, None), (20, 'µg'), (3, 'mg'), (100, 'mg'), (520, 'µg'), (3, 'mg'), (200, 'mg'), (1650, 'mg'), (6, 'g'), (0, 'mg'), (1, 'µg'), (40, 'mg'), (0, 'mg'), (850, 'µg'), (1, 'mg'), (0, 'µg'), (49, 'mg'), (0, 'µg'), (6, 'mg'), (22, 'µg'), (866, 'g'), (1, 'mg')],
    #     ['11672', 'Vegetables and Vegetable Products', 'Potato pancakes', '', (320, 'mg'), (278, 'g'), (742, 'mg'), (2, 'mg'), (2677, 'kcal'), (148, 'g'), (33, 'g'), (4, 'µg'), (410, 'µg'), (17, 'mg'), (360, 'mg'), (2600, 'µg'), (17, 'mg'), (1280, 'mg'), (6220, 'mg'), (61, 'g'), (2, 'mg'), (89, 'µg'), (7640, 'mg'), (2, 'mg'), (320, 'µg'), (4, 'mg'), (3, 'µg'), (276, 'mg'), (3, 'µg'), (2, 'mg'), (27, 'µg'), (478, 'g'), (7, 'mg')]
    # ]
    # # fmt: on
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
        find_closest_solution(A, min_requirements)
    elapsed_time = time.process_time() - t
    print("elapsed_time", elapsed_time, "iter/sec:", iterations / elapsed_time)


def real_test():
    # Part 0: Load foods and requirements
    # # fmt: off
    # example_foods1 = [
    #     ['14091', 'Beverages', 'Beverages, almond milk, unsweetened, shelf stable', '', (1840, 'mg'), (13, 'g'), (31, 'mg'), (0, 'mg'), (150, 'kcal'), (10, 'g'), (2, 'g'), (0, None), (10, 'µg'), (3, 'mg'), (60, 'mg'), (400, 'µg'), (1, 'mg'), (90, 'mg'), (670, 'mg'), (4, 'g'), (0, 'mg'), (1, 'µg'), (720, 'mg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (10, 'µg'), (63, 'mg'), (0, 'µg'), (965, 'g'), (1, 'mg')],
    #     ['14355', 'Beverages', 'Beverages, tea, black, brewed, prepared with tap water', '', (0, 'mg'), (3, 'g'), (4, 'mg'), (0, 'mg'), (10, 'kcal'), (0, 'g'), (0, 'g'), (3730, 'µg'), (50, 'µg'), (0, 'mg'), (30, 'mg'), (2190, 'µg'), (0, 'mg'), (10, 'mg'), (370, 'mg'), (0, 'g'), (0, 'mg'), (0, 'µg'), (30, 'mg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (997, 'g'), (0, 'mg')],
    #     ['9024', 'Fruits and Fruit Juices', 'Apricots, canned, juice pack, with skin, solids and liquids', '', (120, 'mg'), (123, 'g'), (18, 'mg'), (1, 'mg'), (480, 'kcal'), (0, 'g'), (16, 'g'), (0, None), (20, 'µg'), (3, 'mg'), (100, 'mg'), (520, 'µg'), (3, 'mg'), (200, 'mg'), (1650, 'mg'), (6, 'g'), (0, 'mg'), (1, 'µg'), (40, 'mg'), (0, 'mg'), (850, 'µg'), (1, 'mg'), (0, 'µg'), (49, 'mg'), (0, 'µg'), (6, 'mg'), (22, 'µg'), (866, 'g'), (1, 'mg')],
    #     ['11672', 'Vegetables and Vegetable Products', 'Potato pancakes', '', (320, 'mg'), (278, 'g'), (742, 'mg'), (2, 'mg'), (2677, 'kcal'), (148, 'g'), (33, 'g'), (4, 'µg'), (410, 'µg'), (17, 'mg'), (360, 'mg'), (2600, 'µg'), (17, 'mg'), (1280, 'mg'), (6220, 'mg'), (61, 'g'), (2, 'mg'), (89, 'µg'), (7640, 'mg'), (2, 'mg'), (320, 'µg'), (4, 'mg'), (3, 'µg'), (276, 'mg'), (3, 'µg'), (2, 'mg'), (27, 'µg'), (478, 'g'), (7, 'mg')]
    # ]
    # # fmt: on
    example_foods, _ = load_subset_of_data(
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

    # Part 1: Find the solution for a known set using error minimization.
    # solution = find_closest_solution(A, min_requirements)
    solution = find_closest_solution3(A, min_requirements, max_requirements)
    print("solution", solution)
    # Multiply this back to see if it's really a solution.
    result = A @ solution
    print("result", result)
    (
        error,
        under_bounds,
        over_bounds,
        is_out_of_bounds,
        under_bounds_str,
        over_bounds_str,
    ) = evaluate_result(result, min_requirements, max_requirements)
    print(error, under_bounds_str, over_bounds_str, is_out_of_bounds)
    print("is_out_of_bounds", is_out_of_bounds)

    # assert not (is_out_of_bounds)

    print("-" * 80)

    # # Part 2: Solve it with the solver
    # x = solve_it(
    #     min_requirements, max_requirements, example_foods, verbose_logging=False
    # )
    # assert len(x) == 1
    # food_quantity = list(x.values())[0]["food_quantity"]
    # sorted_dict = dict(sorted(food_quantity.items(), key=lambda item: int(item[0])))
    # quantities = tuple(sorted_dict.values())
    # print("quantities", quantities)
    # solution = np.array([quantities])
    # solution = solution.T
    # # Now multipy it back to see if it's really a solution
    # result = A @ solution
    # print(result.T)
    # error, under_bounds, over_bounds, is_out_of_bounds = evaluate_result(
    #     result, min_requirements, max_requirements
    # )
    # # print(error, under_bounds, over_bounds, is_out_of_bounds)
    # print("is_out_of_bounds", is_out_of_bounds)
    #
    # print("-" * 80)

    # Part 3: Benchmark the solution finding
    solution = np.array([1227, 804, 3382, 913])
    solution = solution.T
    result = A @ solution
    print(result.T)
    (
        error,
        under_bounds,
        over_bounds,
        is_out_of_bounds,
        under_bounds_str,
        over_bounds_str,
    ) = evaluate_result(result, min_requirements, max_requirements)
    print(error, under_bounds_str, over_bounds_str, is_out_of_bounds)
    print("is_out_of_bounds", is_out_of_bounds)

    import pdb

    pdb.set_trace()


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
    real_test()
    # tests()

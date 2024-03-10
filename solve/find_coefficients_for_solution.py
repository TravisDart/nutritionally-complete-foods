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
from load_data import load_requirements


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


def evaluate_result(solution, min_bound, max_bound):
    error = np.linalg.norm(solution - min_bound)
    under_bounds = [solution[x] < min_bound[x] for x in range(len(max_bound))]
    over_bounds = [solution[x] > max_bound[x] for x in range(len(max_bound))]
    is_out_of_bounds = any(under_bounds) or any(over_bounds)
    return error, under_bounds, over_bounds, is_out_of_bounds


def benchmark_solving():
    # TODO: un-duplicate this code
    example_foods = [
        [
            "14091",
            "Beverages",
            "Beverages, almond milk, unsweetened, shelf stable",
            "",
            (1840, "mg"),
            (13, "g"),
            (31, "mg"),
            (0, "mg"),
            (150, "kcal"),
            (10, "g"),
            (2, "g"),
            (0, None),
            (10, "µg"),
            (3, "mg"),
            (60, "mg"),
            (400, "µg"),
            (1, "mg"),
            (90, "mg"),
            (670, "mg"),
            (4, "g"),
            (0, "mg"),
            (1, "µg"),
            (720, "mg"),
            (0, "mg"),
            (0, "µg"),
            (0, "mg"),
            (0, "µg"),
            (0, "mg"),
            (10, "µg"),
            (63, "mg"),
            (0, "µg"),
            (965, "g"),
            (1, "mg"),
        ],
        [
            "14355",
            "Beverages",
            "Beverages, tea, black, brewed, prepared with tap water",
            "",
            (0, "mg"),
            (3, "g"),
            (4, "mg"),
            (0, "mg"),
            (10, "kcal"),
            (0, "g"),
            (0, "g"),
            (3730, "µg"),
            (50, "µg"),
            (0, "mg"),
            (30, "mg"),
            (2190, "µg"),
            (0, "mg"),
            (10, "mg"),
            (370, "mg"),
            (0, "g"),
            (0, "mg"),
            (0, "µg"),
            (30, "mg"),
            (0, "mg"),
            (0, "µg"),
            (0, "mg"),
            (0, "µg"),
            (0, "mg"),
            (0, "µg"),
            (0, "mg"),
            (0, "µg"),
            (997, "g"),
            (0, "mg"),
        ],
        [
            "9024",
            "Fruits and Fruit Juices",
            "Apricots, canned, juice pack, with skin, solids and liquids",
            "",
            (120, "mg"),
            (123, "g"),
            (18, "mg"),
            (1, "mg"),
            (480, "kcal"),
            (0, "g"),
            (16, "g"),
            (0, None),
            (20, "µg"),
            (3, "mg"),
            (100, "mg"),
            (520, "µg"),
            (3, "mg"),
            (200, "mg"),
            (1650, "mg"),
            (6, "g"),
            (0, "mg"),
            (1, "µg"),
            (40, "mg"),
            (0, "mg"),
            (850, "µg"),
            (1, "mg"),
            (0, "µg"),
            (49, "mg"),
            (0, "µg"),
            (6, "mg"),
            (22, "µg"),
            (866, "g"),
            (1, "mg"),
        ],
        [
            "11672",
            "Vegetables and Vegetable Products",
            "Potato pancakes",
            "",
            (320, "mg"),
            (278, "g"),
            (742, "mg"),
            (2, "mg"),
            (2677, "kcal"),
            (148, "g"),
            (33, "g"),
            (4, "µg"),
            (410, "µg"),
            (17, "mg"),
            (360, "mg"),
            (2600, "µg"),
            (17, "mg"),
            (1280, "mg"),
            (6220, "mg"),
            (61, "g"),
            (2, "mg"),
            (89, "µg"),
            (7640, "mg"),
            (2, "mg"),
            (320, "µg"),
            (4, "mg"),
            (3, "µg"),
            (276, "mg"),
            (3, "µg"),
            (2, "mg"),
            (27, "µg"),
            (478, "g"),
            (7, "mg"),
        ],
    ]
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
    return


def real_test():
    # Test 2: Square A
    # fmt: off
    # A = np.array([
    #     [1840, 13, 31, 0, 150, 10, 2, 0, 10, 3, 60, 400, 1, 90, 670, 4, 0, 1, 720, 0, 0, 0, 0, 0, 10, 63, 0, 965, 1],
    #     [0, 3, 4, 0, 10, 0, 0, 3730, 50, 0, 30, 2190, 0, 10, 370, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 0, 0, 997, 0],
    #     [130, 110, 56, 1, 460, 4, 16, 0, 50, 5, 90, 570, 1, 160, 1240, 9, 0, 0, 10, 0, 440, 1, 0, 17, 0, 1, 15, 872, 1],
    #     [320, 278, 742, 2, 2677, 148, 33, 4, 410, 17, 360, 2600, 17, 1280, 6220, 61, 2, 89, 7640, 2, 320, 4, 3, 276, 3, 2, 27, 478, 7]
    # ])

    example_foods = [
        ['14091', 'Beverages', 'Beverages, almond milk, unsweetened, shelf stable', '', (1840, 'mg'), (13, 'g'), (31, 'mg'), (0, 'mg'), (150, 'kcal'), (10, 'g'), (2, 'g'), (0, None), (10, 'µg'), (3, 'mg'), (60, 'mg'), (400, 'µg'), (1, 'mg'), (90, 'mg'), (670, 'mg'), (4, 'g'), (0, 'mg'), (1, 'µg'), (720, 'mg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (10, 'µg'), (63, 'mg'), (0, 'µg'), (965, 'g'), (1, 'mg')],
        ['14355', 'Beverages', 'Beverages, tea, black, brewed, prepared with tap water', '', (0, 'mg'), (3, 'g'), (4, 'mg'), (0, 'mg'), (10, 'kcal'), (0, 'g'), (0, 'g'), (3730, 'µg'), (50, 'µg'), (0, 'mg'), (30, 'mg'), (2190, 'µg'), (0, 'mg'), (10, 'mg'), (370, 'mg'), (0, 'g'), (0, 'mg'), (0, 'µg'), (30, 'mg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (0, 'mg'), (0, 'µg'), (997, 'g'), (0, 'mg')],
        ['9024', 'Fruits and Fruit Juices', 'Apricots, canned, juice pack, with skin, solids and liquids', '', (120, 'mg'), (123, 'g'), (18, 'mg'), (1, 'mg'), (480, 'kcal'), (0, 'g'), (16, 'g'), (0, None), (20, 'µg'), (3, 'mg'), (100, 'mg'), (520, 'µg'), (3, 'mg'), (200, 'mg'), (1650, 'mg'), (6, 'g'), (0, 'mg'), (1, 'µg'), (40, 'mg'), (0, 'mg'), (850, 'µg'), (1, 'mg'), (0, 'µg'), (49, 'mg'), (0, 'µg'), (6, 'mg'), (22, 'µg'), (866, 'g'), (1, 'mg')],
        ['11672', 'Vegetables and Vegetable Products', 'Potato pancakes', '', (320, 'mg'), (278, 'g'), (742, 'mg'), (2, 'mg'), (2677, 'kcal'), (148, 'g'), (33, 'g'), (4, 'µg'), (410, 'µg'), (17, 'mg'), (360, 'mg'), (2600, 'µg'), (17, 'mg'), (1280, 'mg'), (6220, 'mg'), (61, 'g'), (2, 'mg'), (89, 'µg'), (7640, 'mg'), (2, 'mg'), (320, 'µg'), (4, 'mg'), (3, 'µg'), (276, 'mg'), (3, 'µg'), (2, 'mg'), (27, 'µg'), (478, 'g'), (7, 'mg')]
    ]
    just_matrix_coefficients = [[y[0] for y in x[4:]] for x in example_foods]
    A = np.array(just_matrix_coefficients)
    A = A.T
    min_requirements, max_requirements, _ = load_requirements()



    example_solution = np.array([[2759, 1199, 804, 1006]])
    print(example_solution.shape)
    print(A.shape)
    example_result = example_solution @ A
    print(example_result.T)

    error, under_bounds, over_bounds, is_out_of_bounds = evaluate_result(
        example_result, min_requirements, max_requirements
    )
    print(error, under_bounds, over_bounds, is_out_of_bounds)

    return


    print("min_requirements", min_requirements)
    print("max_requirements", max_requirements)
    computed_solution = find_closest_solution(A, min_requirements)
    print(example_solution.shape)
    print(A.shape)
    assert(computed_solution.shape == example_solution.shape)
    example_result = A @ example_solution
    print("example_result", example_result)

    computed_result = A @ computed_solution
    print("computed_result", computed_result)
    error, under_bounds, over_bounds, is_out_of_bounds = evaluate_result(
        example_result, min_requirements, max_requirements
    )
    print(error, under_bounds, over_bounds, is_out_of_bounds)
    assert not(is_out_of_bounds)


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

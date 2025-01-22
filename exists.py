import numpy as np
from scipy.optimize import linprog
import time

from constants import FOOD_OFFSET
from solver.initialize import initialize
from solver.load_data import load_requirements

from itertools import combinations


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
        b_ub=np.hstack((A, C)),
        method="highs",
    )

    return result.success


def iterate_over_combos(food_ids, num_foods):
    for x in range(len(food_ids) + 1):
        for y in combinations(food_ids, min(x, num_foods)):
            if y != ():
                yield y


def find_all():
    # fmt: off
    food_ids = [
        35205, 11525, 11270, 9009, 4058, 11946, 11987, 11458, 16001, 11637, 11939, 20076, 2041, 2028, 35074,
        16062, 16076, 42200, 16055, 12169, 11625, 4047, 11977, 11297, 20003, 11230, 4583, 43146, 16067,
        2003, 4534, 11291, 11097, 12171, 16111, 11591, 11276, 11819, 11976, 20072, 4044, 16396, 4511, 4060,
        11161, 2012, 16085, 12029, 4531, 12163, 35093, 11003, 16390, 11086, 4582, 4506, 11087, 11683, 11432,
        4541, 11292, 11982, 2022, 11269, 2015, 2044, 11277, 9139, 2023, 11152, 11165, 4584, 16019, 4588,
        12078, 2066, 4536, 14353, 2009, 35207, 11112, 11660, 11268, 11162, 20077, 11941, 12023, 16078,
        12198, 11588, 16389, 9148, 20138, 35196, 35232, 12698, 11026, 20078, 11334, 12024, 11993, 11952,
        11419, 11113, 11245, 4581, 2007, 4516, 11529, 2013, 11953, 11506, 2033, 11936, 4517, 9002, 11271,
        11158, 4502, 11208, 9244, 11569, 11214, 4053, 11027, 4529, 16080, 35194, 9221, 11239, 16133, 12174,
        11098, 11467, 11937, 9041, 4042, 12170, 11667, 16392, 11234, 20027, 4501, 11931, 11974, 4528, 9129,
        2024, 11240, 9116, 11293, 2046, 2017, 9001, 11967, 12006, 42231, 11203, 12012, 11938, 2016, 11023,
        11300, 12040, 20015, 9147, 20068, 16112, 4055, 4514, 9289, 2021, 20071, 43143, 11530, 11333, 11979,
        4518, 2029, 4513, 16135, 2047, 11998, 16394, 4038, 12036, 12193, 4515, 2038, 4037, 11988, 16060,
        9183, 9165, 2010, 43365, 11141, 11096, 4530, 12037, 16108, 2011, 2020, 4572, 11983, 12005, 11207,
        2042, 11301, 2006, 11955, 11052, 2027, 12039, 16091, 12220, 11099, 11284, 2014, 2039, 16056, 11663,
        2043, 16116, 48052, 4573, 11505, 12038, 11527, 16410, 11670, 11147, 11204, 31019, 4669, 2036, 14368,
        11233, 11110, 35203, 2037, 11090, 16132, 4510, 11962, 11978, 12160, 4532, 2008, 11957, 11615, 20060,
        11242, 2031, 11148, 16115
    ]

    (
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        verbose,
        _,  # num_foods (not applicable for this solver)
    ) = initialize(only_these_ids=food_ids, verbose=False)

    min_requirements = np.array(min_requirements)
    max_requirements = np.array(max_requirements)

    num_foods = 4

    foods = {  # Map Food ID to the food's nutrient values
        f[0]: f[FOOD_OFFSET:] for f in foods
    }
    solutions = set()
    loop_counter = 0
    for combination in iterate_over_combos(food_ids, num_foods):
        loop_counter += 1
        if loop_counter % 1000 == 0:
            print(f"Loop counter: {loop_counter}")

        combo_list = [foods[i] for i in combination]
        good_solution = solution_exists(
            A=min_requirements,
            B=np.transpose(np.array(combo_list)),
            C=max_requirements,
        )
        if good_solution:
            print("Good solution found!", combination)
            solutions.add(combination)
    
    print("Solutions found:", solutions)


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


def known_bad_solution():
    is_good = solution_exists(
        A=np.array([1, 1, 1]),
        B=np.transpose(np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])),
        C=np.array([10, 10, 10]),
    )
    print("good_solution?", is_good)


if __name__ == "__main__":
    # known_solution()
    # find_all()
    known_bad_solution()

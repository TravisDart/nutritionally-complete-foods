import numpy as np
from scipy.optimize import linprog
import time

from constants import FOOD_OFFSET
from solver.initialize import initialize
from solver.load_data import load_requirements


def solution_exists(A, B, C, cc_dim):
    """
    Check if there exists a solution to the linear programming problem A <= Bx <= C

    :param A: Lower bound
    :param B: Matrix of coefficients
    :param C: Upper bound
    :return: Boolean indicating if a solution exists
    """
    # print(A)
    # print(B)
    # print(C)
    #
    # print(np.ones(len(A)))
    # print(np.vstack((B, -B)))
    # print(np.hstack((A, C)))
    # import pdb
    #
    # pdb.set_trace()
    # Solve the linear programming problem using linprog with 'highs' method
    result = linprog(
        # The objective function (any objective function will do, we just care that the inequality holds)
        c=np.ones(cc_dim),
        # Define the equality constraints (Bx - s1 = A and Bx + s2 = C)
        A_ub=np.vstack((B, -B)),
        b_ub=np.hstack((A, C)),
        method="highs",
    )

    return result.success
    # # Print the results
    # if result.success:
    #     print("Optimal solution found:")
    #     print("x:", result.x)  # Extract x values
    #     print(
    #         "Objective function value:",
    #         AtA - 2 * np.dot(AtB, result.x) + np.dot(result.x, np.dot(BtB, result.x)),
    #     )
    # else:
    #     print("Solver did not converge.")


if __name__ == "__main__":
    # fmt: off
    # top_foods = [
    #     35205, 11525, 11270, 9009, 4058, 11946, 11987, 11458, 16001, 11637, 11939, 20076, 2041, 2028, 35074,
    #     16062, 16076, 42200, 16055, 12169, 11625, 4047, 11977, 11297, 20003, 11230, 4583, 43146, 16067,
    #     2003, 4534, 11291, 11097, 12171, 16111, 11591, 11276, 11819, 11976, 20072, 4044, 16396, 4511, 4060,
    #     11161, 2012, 16085, 12029, 4531, 12163, 35093, 11003, 16390, 11086, 4582, 4506, 11087, 11683, 11432,
    #     4541, 11292, 11982, 2022, 11269, 2015, 2044, 11277, 9139, 2023, 11152, 11165, 4584, 16019, 4588,
    #     12078, 2066, 4536, 14353, 2009, 35207, 11112, 11660, 11268, 11162, 20077, 11941, 12023, 16078,
    #     12198, 11588, 16389, 9148, 20138, 35196, 35232, 12698, 11026, 20078, 11334, 12024, 11993, 11952,
    #     11419, 11113, 11245, 4581, 2007, 4516, 11529, 2013, 11953, 11506, 2033, 11936, 4517, 9002, 11271,
    #     11158, 4502, 11208, 9244, 11569, 11214, 4053, 11027, 4529, 16080, 35194, 9221, 11239, 16133, 12174,
    #     11098, 11467, 11937, 9041, 4042, 12170, 11667, 16392, 11234, 20027, 4501, 11931, 11974, 4528, 9129,
    #     2024, 11240, 9116, 11293, 2046, 2017, 9001, 11967, 12006, 42231, 11203, 12012, 11938, 2016, 11023,
    #     11300, 12040, 20015, 9147, 20068, 16112, 4055, 4514, 9289, 2021, 20071, 43143, 11530, 11333, 11979,
    #     4518, 2029, 4513, 16135, 2047, 11998, 16394, 4038, 12036, 12193, 4515, 2038, 4037, 11988, 16060,
    #     9183, 9165, 2010, 43365, 11141, 11096, 4530, 12037, 16108, 2011, 2020, 4572, 11983, 12005, 11207,
    #     2042, 11301, 2006, 11955, 11052, 2027, 12039, 16091, 12220, 11099, 11284, 2014, 2039, 16056, 11663,
    #     2043, 16116, 48052, 4573, 11505, 12038, 11527, 16410, 11670, 11147, 11204, 31019, 4669, 2036, 14368,
    #     11233, 11110, 35203, 2037, 11090, 16132, 4510, 11962, 11978, 12160, 4532, 2008, 11957, 11615, 20060,
    #     11242, 2031, 11148, 16115
    # ]
    top_foods = [
        9009, 11268, 11284, 4531, 48052, 2007, 11936, 42231, 11615, 42200, 4038, 2047, 9289, 2017, 4532, 11667,
        12169, 16390
    ]
    # fmt: on

    (
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        verbose,
        _,  # num_foods (not applicable for this solver)
    ) = initialize(only_these_ids=top_foods, verbose=False)

    i = 3
    just_numbers = [f[FOOD_OFFSET:][:i] for f in foods]
    # start_time = time.time()
    # for _ in range(10000):

    # Works
    # solution_exists(
    #     A=np.array([1, 1, 1]),
    #     B=np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
    #     C=np.array([10, 10, 10]),
    # )

    # a_dim, b_dim1, b_dim2, c_dim, cc_dim = (3, 3, 3, 3, 3)  # Works
    # a_dim, b_dim1, b_dim2, c_dim, cc_dim = (4, 4, 4, 4, 4)  # Works
    a_dim, b_dim1, b_dim2, c_dim, cc_dim = (4, 5, 4, 4, 5)  # Works
    solution_exists(
        A=np.array([0] * a_dim),
        B=np.array([[0] * b_dim1] * b_dim2),
        C=np.array([10] * c_dim),
        cc_dim=cc_dim,
    )

    # print(min_requirements[:i])
    # print(just_numbers)
    # print(max_requirements[:i])

    # solution_exists(
    #     A=np.array(min_requirements[:i]),
    #     B=np.array(just_numbers),
    #     C=np.array(max_requirements[:i]),
    # )

    # end_time = time.time()
    # print(f"Total execution time for 10,000 runs: {end_time - start_time} seconds")

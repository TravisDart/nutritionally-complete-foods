from typing import List

from ortools.sat.python import cp_model

from constants import FOOD_OFFSET
from solver.initialize import initialize
from solver.solution_printer import VarArraySolutionPrinter, print_info


def solve_it(
    foods,
    max_qty: List[int],
    min_requirements: List[int],
    max_requirements: List[int],
    log_level: int = 0,
):
    """
    :param min_requirements a list containing the lower bound of nutritional requirements.
    :param max_requirements a list containing the upper bound of nutritional requirements.
    :param foods: A list specifying the nutritional value of each food.
    :param num_foods: Restrict the solution to only use this many foods.
    :param log_level: 0 = No logging, 1 = Log solution status, 2 = Log solution status and solver progress.
    :return: A list of solutions.
    """
    model = cp_model.CpModel()

    # If the data file and nutritional requirements are static,
    # then food_max_value and max_error could be cached somewhere.
    quantity_of_food = [
        model.NewIntVar(0, max_qty[i], name=str(food[0]))
        for i, food in enumerate(foods)
    ]
    for i in range(len(min_requirements)):
        nutrient_intake = sum(
            food[i + FOOD_OFFSET] * quantity_of_food[j]  # intermediate_values[j]
            for j, food in enumerate(foods)
        )
        model.AddLinearConstraint(  # min_requirements[i] <= nutrient_intake <= max_requirements[i]
            nutrient_intake, min_requirements[i], max_requirements[i]
        )

    model.Minimize(sum(quantity_of_food))

    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = bool(log_level >= 2)
    solver.parameters.enumerate_all_solutions = True
    solution_printer = VarArraySolutionPrinter(quantity_of_food)

    status = solver.Solve(model, solution_printer)
    if log_level >= 1:
        print_info(status, solver, solution_printer)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        solutions = solution_printer.get_solutions()
        if log_level:
            print(solutions)
        return solutions


if __name__ == "__main__":
    # fmt: off
    top_foods = [
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
    # fmt: on
    top_foods = [
        2009,
        9221,
        12038,
        11939,
    ]

    (
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        verbose,
        _,  # num_foods (not applicable for this solver)
    ) = initialize(only_these_ids=top_foods)

    solutions = solve_it(
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        log_level=verbose,
    )
    print(solutions)

    for solution in solutions.values():
        s2 = solution["food_quantity"]

        # reverse sort by the 2nd element of the tuple
        sorted_solution = sorted(s2.items(), key=lambda x: x[1], reverse=True)
        for food in sorted_solution:
            print(food, [f[1] for f in foods if f[0] == int(food[0])])
        print("total_quantity:", solution["total_quantity"])
        print("-" * 10)

    print(solutions)

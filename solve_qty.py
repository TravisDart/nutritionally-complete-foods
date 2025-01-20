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
        35205, 11525, 11270, 9009, 4058, 11946, 11987, 11458, 11303, 16001, 11637, 11939, 20076, 2041, 2028,
        11575, 35074, 16062, 16076, 42200, 11821, 16055, 12169, 11625, 4047, 11977, 11062, 2054, 11297,
        20003, 11230, 4583, 43146, 16067, 2003, 4534, 11291, 11097, 12171, 16111, 11591, 11276, 11819,
        11976, 20072, 4044, 16396, 4511, 4060, 11161, 2012, 9219, 11724, 16085, 12029, 4531, 12163, 11236,
        35093, 11003, 16390, 11086, 9119, 4582, 4506, 11087, 11683, 11432, 4541, 11292, 11982, 2022, 11273,
        11269, 11916, 2015, 2044, 11277, 9139, 9544, 31034, 11285, 2023, 11886, 11464, 11152, 11165, 4584,
        16019, 4588, 12078, 11156, 11885, 11921, 2066, 4536, 14353, 2009, 35207, 11112, 11660, 11335, 11268,
        11162, 11940, 20077, 11941, 12023, 9125, 16078, 12198, 11943, 11588, 16389, 9148, 20138, 35196,
        35232, 12698, 11026, 20078, 11334, 12024, 11993, 11952, 11419, 11113, 11245, 4581, 2007, 4516,
        11529, 11953, 11531, 11506, 11164, 2033, 11936, 4517, 9002, 11271, 11158, 4502, 11208, 9244, 11569,
        11214, 4053, 11027, 4529, 16080, 35194, 9221, 11239, 16133, 12174, 11098, 11467, 11937, 9041, 4042,
        12170, 11667, 16392, 11234, 16120, 20027, 4501, 11931, 11974, 4528, 9129, 2024, 11240, 9116, 11095,
        11293, 2017, 9001, 11967, 12006, 42231, 11203, 12012, 11938, 2016, 11023, 11300, 12040, 20015, 9147,
        20068, 16129, 16112, 11235, 4055, 4514, 9289, 2021, 20071, 43143, 11530, 11333, 11517, 11979, 4518,
        2029, 4513, 9123, 11945, 11855, 16135, 2047, 11998, 16394, 4038, 12036, 12193, 4515, 2038, 4037,
        11988, 16060, 9183, 9165, 2010, 43365, 11141, 11096, 11056, 11975, 4530, 12037, 16108, 2011, 2020,
        4572, 11329, 11983, 12005, 11577, 11205, 11207, 11632, 2042, 11301, 2006, 11955, 11052, 2027, 12039,
        16091, 12220, 11099, 11284, 2014, 2039, 16056, 43387, 11663, 2043, 16116, 48052, 4573, 11505, 12038,
        11527, 16410, 11537, 11670, 11147, 11204, 31019, 4669, 2036, 16128, 14368, 11233, 11109, 11110,
        11220, 35203, 2037, 11090, 16132, 4510, 11962, 11978, 12160, 4532, 11459, 2008, 11957, 11615, 11461,
        20060, 11242, 2031, 11148, 16115
    ]
    # fmt: on

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

    # fmt: off
    # solutions = {(2007, 2047, 4038, 4531, 9009, 9289, 11268, 11284, 11615, 11624, 11663, 11667, 11936, 12169, 12170, 16128, 16133, 20027, 31019, 35234, 42200, 42231, 43387, 43476, 48052): {'food_quantity': {'2007': 26, '2047': 2, '4038': 4, '4531': 81, '9009': 333, '9289': 3, '11268': 84, '11284': 8, '11615': 26, '11624': 39, '11663': 1, '11667': 1, '11936': 37, '12169': 29, '12170': 5, '16128': 1, '16133': 1, '20027': 1, '31019': 2, '35234': 1, '42200': 6, '42231': 1, '43387': 1, '43476': 1, '48052': 49}, 'total_quantity': 743}, (2007, 2047, 4038, 4531, 9009, 11268, 11615, 11624, 11663, 11667, 11936, 12114, 12169, 12170, 16128, 16133, 20027, 35234, 42200, 42231, 48052): {'food_quantity': {'2007': 33, '2047': 2, '4038': 4, '4531': 79, '9009': 319, '11268': 91, '11615': 26, '11624': 48, '11663': 2, '11667': 1, '11936': 37, '12114': 14, '12169': 15, '12170': 3, '16128': 4, '16133': 2, '20027': 3, '35234': 1, '42200': 11, '42231': 1, '48052': 45}, 'total_quantity': 741}, (2007, 2009, 2024, 2047, 4038, 4531, 9009, 9289, 11268, 11413, 11615, 11624, 11667, 11936, 11993, 12169, 12170, 16078, 20028, 20088, 35131, 35232, 42200, 48052): {'food_quantity': {'2007': 27, '2009': 1, '2024': 1, '2047': 2, '4038': 3, '4531': 82, '9009': 330, '9289': 5, '11268': 83, '11413': 1, '11615': 26, '11624': 42, '11667': 1, '11936': 36, '11993': 1, '12169': 29, '12170': 5, '16078': 1, '20028': 1, '20088': 4, '35131': 1, '35232': 1, '42200': 10, '48052': 47}, 'total_quantity': 740}}
    # fmt: on

    for solution in solutions.values():
        s2 = solution["food_quantity"]

        # reverse sort by the 2nd element of the tuple
        sorted_solution = sorted(s2.items(), key=lambda x: x[1], reverse=True)
        for food in sorted_solution:
            print(food, [f[1] for f in foods if f[0] == int(food[0])])
        print("-" * 10)

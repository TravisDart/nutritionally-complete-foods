from typing import List

from ortools.sat.python import cp_model

from constants import FOOD_OFFSET, TOP_FOODS
from solver.initialize import initialize
from solver.solution_printer import MultipleSolutionPrinter, print_info


def solve_minimal_quantity(
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
    solution_printer = MultipleSolutionPrinter(quantity_of_food)

    status = solver.Solve(model, solution_printer)
    if log_level >= 1:
        print_info(status, solver, solution_printer)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        solutions = solution_printer.get_solutions()
        if log_level:
            print(solutions)
        return solutions


if __name__ == "__main__":
    TOP_FOODS = [
        2009,  # Spices and Herbs > Spices, chili powder
        9221,  # Fruits and Fruit Juices > Tangerine juice, raw
        12038,  # Nut and Seed Products > Seeds, sunflower seed kernels, oil roasted, without salt
        # And one type of mushroom:
        # 11939,  # Vegetables and Vegetable Products > Mushrooms, portabella, exposed to ultraviolet light, grilled
        # 11993,  # Vegetables and Vegetable Products > Mushrooms, maitake, raw
        # 11936,  # Vegetables and Vegetable Products > Mushrooms, brown, italian, or crimini, exposed to ultraviolet light, raw
        11938,  # Vegetables and Vegetable Products > Mushroom, white, exposed to ultraviolet light, raw
    ]

    (
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        verbose,
        _,  # num_foods (not applicable for this solver)
    ) = initialize(only_these_ids=TOP_FOODS)

    solutions = solve_minimal_quantity(
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

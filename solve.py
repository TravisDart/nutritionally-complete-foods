from typing import List

from ortools.sat.python import cp_model

from constants import FOOD_OFFSET
from solver.find_n_greatest import find_max_error
from solver.initialize import initialize
from solver.solution_printer import (
    SingleSolutionPrinter,
    print_info,
    MultipleSolutionPrinter,
)


def solve_it(
    foods,
    max_qty: List[int],
    min_requirements: List[int],
    max_requirements: List[int],
    num_foods: int,
    log_level: int = 0,
    return_multiple_solutions: bool = True,
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
    max_error = find_max_error(foods, max_qty, num_foods, min_requirements)
    quantity_of_food = [
        model.NewIntVar(0, max_qty[i], name=str(food[0]))
        for i, food in enumerate(foods)
    ]
    intermediate_values = [
        model.NewIntVar(0, max_qty[i], name=str(food[0]))
        for i, food in enumerate(foods)
    ]
    error_for_quantity = [
        model.NewIntVar(0, max_error[i], f"Error {nutrient}")
        for i, nutrient in enumerate(min_requirements)
    ]
    should_use_food = [model.NewIntVar(0, 1, name=str(food[0])) for food in foods]

    for j in range(len(foods)):
        model.AddMultiplicationEquality(
            intermediate_values[j], quantity_of_food[j], should_use_food[j]
        )

    model.Add(sum(should_use_food) == num_foods)

    for i in range(len(min_requirements)):
        nutrient_intake = sum(
            food[i + FOOD_OFFSET] * intermediate_values[j]
            for j, food in enumerate(foods)
        )
        model.AddLinearConstraint(  # min_requirements[i] <= nutrient_intake <= max_requirements[i]
            nutrient_intake, min_requirements[i], max_requirements[i]
        )
        # Here we apply the traditional metric for error using absolute value:
        model.AddAbsEquality(
            target=error_for_quantity[i], expr=nutrient_intake - min_requirements[i]
        )

    model.Minimize(sum(error_for_quantity))

    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = bool(log_level >= 2)
    solver.parameters.enumerate_all_solutions = True
    if return_multiple_solutions:
        solution_printer = MultipleSolutionPrinter(intermediate_values)
    else:
        solution_printer = SingleSolutionPrinter(intermediate_values)

    status = solver.Solve(model, solution_printer)
    if log_level >= 1:
        print_info(status, solver, solution_printer)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        result = solution_printer.get_solutions()
        if log_level:
            print(result)
        return result


if __name__ == "__main__":
    (
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        verbose,
        num_foods,
    ) = initialize()

    if num_foods is None:
        num_foods_range = range(1, 8)
    else:
        num_foods_range = [num_foods]

    for num_foods in num_foods_range:
        print(f"Looking for solutions with {num_foods} food(s)")
        solutions = solve_it(
            foods,
            max_foods,
            min_requirements,
            max_requirements,
            num_foods=num_foods,
            log_level=verbose,
            return_multiple_solutions=True,
        )
        print(solutions)

from pprint import pprint
from statistics import mean
from typing import List

from ortools.sat.python import cp_model

from constants import FOOD_OFFSET
from data.download_data import download_data_if_needed
from solver.find_n_greatest import find_max_error
from solver.initialize import initialize
from solver.load_data import load_data
from solver.utils import get_arg_parser


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables, error_for_quantity):
        super().__init__()
        self.__variables = variables
        self.__error_for_quantity = error_for_quantity
        self.__solution = None

    def get_solution(self):
        return self.__solution

    def on_solution_callback(self):
        # Just the ordered IDs of the foods in the solution.
        self.__solution = tuple(
            sorted([int(v.Name()) for v in self.__variables if self.Value(v) != 0])
        )
        self.StopSearch()


def print_info(status, solver, solution_printer):
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("\nStatistics")
        print(f"  status   : {solver.StatusName(status)}")
        print(f"  conflicts: {solver.NumConflicts()}")
        print(f"  branches : {solver.NumBranches()}")
        print(f"  wall time: {solver.WallTime()} s")
        print(f"  sol found: {solution_printer.get_solution()}")
    else:
        outcomes = [
            "UNKNOWN",
            "MODEL_INVALID",
            "FEASIBLE",
            "INFEASIBLE",
            "OPTIMAL",
        ]
        outcome = outcomes[status]
        print(outcome)


def solve_it(
    foods,
    max_qty: List[int],
    min_requirements: List[int],
    max_requirements: List[int],
    num_foods: int,
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
    solution_printer = VarArraySolutionPrinter(intermediate_values, error_for_quantity)

    status = solver.Solve(model, solution_printer)
    if log_level >= 1:
        print_info(status, solver, solution_printer)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        solution = solution_printer.get_solution()
        if log_level:
            print(solution)
        return solution


if __name__ == "__main__":
    foods, max_foods, min_requirements, max_requirements, verbose = initialize()

    solutions = solve_it(
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        num_foods=7,
        log_level=verbose,
    )
    print(solutions)

    # num_foods = 1
    # solutions = []
    # while not solutions:
    #     solutions = solve_it(
    #         min_requirements,
    #         max_requirements,
    #         foods,
    #         num_foods=num_foods,
    #         log_level=args.verbose,
    #     )
    #
    #     if solutions:
    #         break
    #     else:
    #         print(f"No solutions with {num_foods} foods found.")
    #         # If we specify the number of solutions as a command-line argument,
    #         # then don't loop; stop after trying that number.
    #         if args.n is not None:
    #             break
    #         else:
    #             num_foods += 1

import sys
from itertools import combinations
from pprint import pprint
from statistics import mean

from tqdm import tqdm

from constants import FOOD_OFFSET, MAX_NUMBER, NUMBER_SCALE
from load_data import load_data
from ortools.sat.python import cp_model
from utils import get_arg_parser


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(
        self,
        variables,
        min_requirements,
        max_requirements,
        foods,
        error_for_quantity,
        log_level: int = 0,
        solutions_to_keep=float("inf"),
    ):
        super().__init__()
        self.__variables = variables
        self.__foods = foods
        self.__min_requirements = min_requirements
        self.__max_requirements = max_requirements
        self.__error_for_quantity = error_for_quantity

        self.__solutions_to_keep = solutions_to_keep
        self.__solutions = {}
        self.__log_level = log_level

    def get_solutions(self):
        return self.__solutions

    def on_solution_callback(self):
        food_ids = tuple(
            sorted([int(v.Name()) for v in self.__variables if self.Value(v) != 0])
        )
        solution = {
            "food_quantity": {
                v.Name(): self.Value(v) for v in self.__variables if self.Value(v) != 0
            },
            "avg_error": mean([self.Value(v) for v in self.__error_for_quantity]),
            "total_error": sum([self.Value(v) for v in self.__error_for_quantity]),
        }

        # If we already have this combination of foods, pick the one with the lowest error.
        if food_ids in self.__solutions:
            if solution["total_error"] < self.__solutions[food_ids]["total_error"]:
                if self.__log_level >= 1:
                    print("Found more optimal solution for", food_ids)
                    print("Old solution:", self.__solutions[food_ids])
                    print("New solution:", solution)
                self.__solutions[food_ids] = solution
        else:
            self.__solutions[food_ids] = solution
            if self.__log_level >= 1:
                print("Found a new solution:", food_ids)

        # By default, solutions_to_keep is infinite. But if it's set, then only keep the best solutions.
        if len(self.__solutions) >= self.__solutions_to_keep:
            max_error_key = max(
                self.__solutions,
                key=lambda key: self.__solutions[key].get("total_error", 0),
            )
            del self.__solutions[max_error_key]
            if self.__log_level >= 1:
                print("Deleted old solution:", max_error_key)


def print_info(status, solver, solution_printer):
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("\nStatistics")
        print(f"  status   : {solver.StatusName(status)}")
        print(f"  conflicts: {solver.NumConflicts()}")
        print(f"  branches : {solver.NumBranches()}")
        print(f"  wall time: {solver.WallTime()} s")
        print(f"  sol found: {len(solution_printer.get_solutions())}")
    # I'm pretty sure this used to work...
    # elif status == cp_model.MODEL_INVALID:
    #     print(cp_model.Validate())
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
    min_requirements,
    max_requirements,
    foods,
    num_foods: int = 4,
    required_foods: list[int] = [],
    log_level: int = 0,
):
    """
    :param min_requirements a list containing the lower bound of nutritional requirements.
    :param max_requirements a list containing the upper bound of nutritional requirements.
    :param foods: A list specifying the nutritional value of each food.
    :param num_foods: Restrict the solution to only use this many foods.
    :param required_foods: A list of foods that must be in the solution.
    :param log_level: 0 = No logging, 1 = Log solution status, 2 = Log solution status and solver progress.
    :return: A list of solutions.
    """
    model = cp_model.CpModel()

    quantity_of_food = [
        model.NewIntVar(0, MAX_NUMBER * NUMBER_SCALE, food[2]) for food in foods
    ]
    error_for_quantity = [
        model.NewIntVar(0, MAX_NUMBER * NUMBER_SCALE, f"Error {nutrient}")
        for nutrient in min_requirements
    ]
    if num_foods:
        should_use_food = [model.NewIntVar(0, 1, name=str(food[0])) for food in foods]
        intermediate_values = [
            model.NewIntVar(0, MAX_NUMBER * NUMBER_SCALE, name=str(food[0]))
            for food in foods
        ]

        for j in range(len(foods)):
            model.AddMultiplicationEquality(
                intermediate_values[j], quantity_of_food[j], should_use_food[j]
            )

        for k in required_foods:
            model.Add(should_use_food[k] == 1)

        model.Add(sum(should_use_food) == num_foods)
        solver_vars = intermediate_values
    else:
        solver_vars = quantity_of_food

    for i in range(len(min_requirements)):
        nutrient_intake = sum(
            food[i + FOOD_OFFSET][0] * solver_vars[j] for j, food in enumerate(foods)
        )
        model.AddLinearConstraint(
            nutrient_intake, min_requirements[i], max_requirements[i]
        )
        # Here we apply the traditional metric for error using absolute value:
        model.AddAbsEquality(
            target=error_for_quantity[i], expr=nutrient_intake - min_requirements[i]
        )
        # Supposedly you don't need abs. I guess because the two expressions are always positive
        # model.Add(error_for_quantity[i] == nutrient_intake - min_requirements[i])

    model.Minimize(sum(error_for_quantity))

    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = bool(log_level >= 2)
    solver.parameters.enumerate_all_solutions = True
    # The solution printer displays the nutrient that is out of bounds.
    solution_printer = VarArraySolutionPrinter(
        solver_vars,
        min_requirements,
        max_requirements,
        foods,
        error_for_quantity,
        log_level=log_level,
    )

    status = solver.Solve(model, solution_printer)
    if log_level >= 1:
        print_info(status, solver, solution_printer)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        solutions = solution_printer.get_solutions()
        if log_level:
            pprint(solutions)
        return solutions


if __name__ == "__main__":
    args = get_arg_parser().parse_args()

    # List of food IDs to exclude. Add new exclusions here.
    # The current list is composed of the processed foods that I have come across during testing.
    # Don't remove foods from selected_foods.txt, as the food IDs will change, breaking the tests and previous solutions
    exclude = [
        35182,  # Acorn stew (Apache)
        14091,  # Beverages, almond milk, unsweetened, shelf stable
        14639,  # Beverages, rice milk, unsweetened
        11656,  # Corn pudding, home prepared
        11672,  # Potato pancakes
    ]

    nutrients, foods, food_labels, min_requirements, max_requirements = load_data(
        should_use_test_data=args.test_data,
        exclude=exclude,
    )

    solutions = solve_it(
        min_requirements,
        max_requirements,
        foods,
        num_foods=args.n,
        log_level=args.verbose,
    )
    print(solutions)

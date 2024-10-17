from pprint import pprint
from statistics import mean

from ortools.sat.python import cp_model

from constants import FOOD_OFFSET, NUMBER_SCALE
from load_data import load_data
from find_n_greatest import find_max_error
from find_max import find_food_max_value
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
    ):
        super().__init__()
        self.__variables = variables
        self.__foods = foods
        self.__min_requirements = min_requirements
        self.__max_requirements = max_requirements
        self.__error_for_quantity = error_for_quantity

        self.__solutions = {}
        self.__log_level = log_level

    def get_solutions(self):
        return self.__solutions

    def on_solution_callback(self):
        # Just the ordered IDs of the foods in the solution.
        solution_id = tuple(
            sorted([int(v.Name()) for v in self.__variables if self.Value(v) != 0])
        )

        # Info on the solution.
        solution_value = {
            "food_quantity": {
                v.Name(): self.Value(v) for v in self.__variables if self.Value(v) != 0
            },
            "avg_error": mean([self.Value(v) for v in self.__error_for_quantity]),
            "total_error": sum([self.Value(v) for v in self.__error_for_quantity]),
        }

        # If we already have this combination of foods, pick the one with the lowest error.
        if solution_id in self.__solutions:
            if (
                solution_value["total_error"]
                < self.__solutions[solution_id]["total_error"]
            ):
                if self.__log_level >= 1:
                    print("Found more optimal solution for", solution_id)
                    print("Old solution:", self.__solutions[solution_id])
                    print("New solution:", solution_value)
                self.__solutions[solution_id] = solution_value
        else:
            self.__solutions[solution_id] = solution_value
            if self.__log_level >= 1:
                print("Found a new solution:", solution_id)


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
    food_values = [[f2[0] for f2 in f1[FOOD_OFFSET:]] for f1 in foods]
    food_max_value = find_food_max_value(food_values, max_requirements, NUMBER_SCALE)
    max_error = find_max_error(food_values, num_foods, min_requirements, NUMBER_SCALE)

    quantity_of_food = [
        model.NewIntVar(0, food_max_value[i], name=str(food[0]))
        for i, food in enumerate(foods)
    ]
    intermediate_values = [
        model.NewIntVar(0, food_max_value[i], name=str(food[0]))
        for i, food in enumerate(foods)
    ]
    # TODO: Fix the calcuation for max_error[i] and use that.
    error_for_quantity = [
        model.NewIntVar(0, 5_000_000, f"Error {nutrient}")
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
            food[i + FOOD_OFFSET][0] * intermediate_values[j]
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
    # The solution printer displays the nutrient that is out of bounds.
    solution_printer = VarArraySolutionPrinter(
        intermediate_values,
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

    nutrients, foods, food_labels, min_requirements, max_requirements = load_data(
        should_use_test_data=args.test_data
    )

    solutions = solve_it(
        min_requirements,
        max_requirements,
        foods,
        num_foods=7,
        log_level=args.verbose,
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

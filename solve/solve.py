import argparse
import time
from itertools import combinations
from pprint import pprint
from statistics import mean

from tqdm import tqdm

from constants import FOOD_OFFSET, MAX_NUMBER, NUMBER_SCALE
from load_data import (
    load_real_data,
    load_requirements,
    load_subset_of_data,
    load_test_data,
)
from ortools.sat.python import cp_model

from validate_input import validate_data


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
    elif status == cp_model.MODEL_INVALID:
        print(cp_model.Validate())
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


def load_data(should_use_test_data=False):
    if should_use_test_data:
        nutrients, foods, food_labels, min_requirements, max_requirements = load_test_data()
    else:
        foods, food_labels = load_real_data()
        # foods, food_labels = load_subset_of_data()
        min_requirements, max_requirements, nutrients = load_requirements()
        validate_data(nutrients, foods, food_labels)

    # List of food IDs to exclude. For a more permanent solution, remove the food from selected_foods.txt
    exclude = []
    foods = [food for food in foods if int(food[0]) not in exclude]

    return nutrients, foods, food_labels, min_requirements, max_requirements


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find sets of foods that combine to satisfy one's daily nutritional requirements."
    )
    parser.add_argument(
        "-n",
        type=int,
        default=8,
        help="The number of foods in the solution set. The default is 8 foods.",
    )
    parser.add_argument(
        "--test-data",
        action="store_true",
        help="Use test data instead of real data.",
    )
    args = parser.parse_args()

    nutrients, foods, food_labels, min_requirements, max_requirements = load_data(should_use_test_data=args.test_data)

    # Step 2: Find solutions
    def first_run(min_requirements, max_requirements, foods, num_foods):
        # Find the initial set of solutions, normally.
        keep_going = True
        all_solutions = {}
        while keep_going:
            solutions = solve_it(
                min_requirements,
                max_requirements,
                foods,
                num_foods,
            )
            print("Solution:", solutions)
            if solutions:
                all_solutions.update(solutions)

                # Remove foods in the solution from the list of foods:
                for solution in dict(solutions).keys():
                    foods = [food for food in foods if int(food[0]) not in solution]
            else:
                keep_going = False

        return all_solutions

    all_solutions = first_run(
        min_requirements,
        max_requirements,
        foods,
        num_foods=args.n,
    )
    # # fmt: off
    # all_solutions = {
    #     (4510, 9520, 11938, 14412, 16112, 31020, 35206): {'food_quantity': {'35206': 1136, '14412': 17835, '4510': 115, '9520': 1035, '16112': 642, '11938': 378, '31020': 241}, 'avg_error': 2161471.7586206896, 'total_error': 62682681},
    #     (4513, 9520, 11938, 14412, 16112, 31020, 35206): {'food_quantity': {'35206': 1160, '14412': 17721, '4513': 115, '9520': 1033, '16112': 644, '11938': 378, '31020': 241}, 'avg_error': 2165449.0689655175, 'total_error': 62798023},
    #     (4588, 9520, 11938, 14412, 16112, 31020, 35206): {'food_quantity': {'35206': 1172, '14412': 17582, '4588': 116, '9520': 1033, '16112': 624, '11938': 289, '31020': 288}, 'avg_error': 2137777.3103448274, 'total_error': 61995542},
    #     (4588, 9282, 9520, 11938, 14412, 16112, 31020): {'food_quantity': {'14412': 15849, '4588': 116, '9520': 1033, '9282': 1718, '16112': 669, '11938': 289, '31020': 242}, 'avg_error': 2013152.2068965517, 'total_error': 58381414},
    #     (4516, 9282, 9520, 11938, 14412, 16112, 31020): {'food_quantity': {'14412': 15849, '4516': 116, '9520': 1033, '9282': 1718, '16112': 669, '11938': 289, '31020': 242}, 'avg_error': 2011588.2068965517, 'total_error': 58336058},
    #     (4581, 9282, 9520, 11938, 14412, 16112, 31020): {'food_quantity': {'14412': 15849, '4581': 116, '9520': 1033, '9282': 1718, '16112': 669, '11938': 289, '31020': 242}, 'avg_error': 2011576.2068965517, 'total_error': 58335710},
    #     (9282, 9520, 11938, 14412, 16112, 31020, 42231): {'food_quantity': {'14412': 15778, '42231': 116, '9520': 1060, '9282': 1684, '16112': 668, '11938': 289, '31020': 243}, 'avg_error': 2009702.3103448276, 'total_error': 58281367},
    #     (4707, 9282, 9520, 11938, 14412, 16112, 31020): {'food_quantity': {'14412': 15800, '4707': 118, '9520': 1077, '9282': 1801, '16112': 621, '11938': 334, '31020': 245}, 'avg_error': 1965344.0344827587, 'total_error': 56994977},
    #     (4707, 9192, 9520, 11938, 14412, 16112, 31020): {'food_quantity': {'14412': 12196, '4707': 108, '9520': 963, '9192': 3805, '16112': 696, '11938': 254, '31020': 250}, 'avg_error': 1927527.1724137932, 'total_error': 55898288},
    #     (4707, 9520, 11993, 14412, 31020, 35206, 43449): {'food_quantity': {'35206': 528, '14412': 11628, '4707': 151, '9520': 1041, '43449': 1419, '11993': 129, '31020': 453}, 'avg_error': 950805.3793103448, 'total_error': 27573356},
    #     (4572, 9520, 11993, 14412, 31020, 35206, 43449): {'food_quantity': {'35206': 513, '14412': 11628, '4572': 149, '9520': 1023, '43449': 1454, '11993': 110, '31020': 459}, 'avg_error': 938185.4137931034, 'total_error': 27207377},
    #     (4516, 9520, 11993, 14412, 31020, 35206, 43449): {'food_quantity': {'35206': 513, '14412': 11628, '4516': 149, '9520': 1023, '43449': 1454, '11993': 110, '31020': 459}, 'avg_error': 938175.1379310344, 'total_error': 27207079},
    #     (4047, 9520, 11993, 14412, 31020, 35206, 43449): {'food_quantity': {'35206': 486, '14412': 11628, '4047': 151, '9520': 1026, '43449': 1446, '11993': 117, '31020': 458}, 'avg_error': 930482.9310344828, 'total_error': 26984005},
    #     (4518, 9520, 11993, 14412, 31020, 35206, 43449): {'food_quantity': {'35206': 473, '14412': 11628, '4518': 150, '9520': 1020, '43449': 1458, '11993': 111, '31020': 460}, 'avg_error': 929052.275862069, 'total_error': 26942516},
    #     (4518, 9520, 11998, 14412, 31020, 35206, 43449): {'food_quantity': {'35206': 447, '14412': 11628, '4518': 149, '9520': 898, '43449': 1569, '11998': 125, '31020': 459}, 'avg_error': 927350.3448275862, 'total_error': 26893160},
    #     (9520, 11998, 14412, 31020, 35092, 35206, 43449): {'food_quantity': {'35206': 439, '35092': 245, '14412': 11628, '9520': 869, '43449': 1471, '11998': 274, '31020': 419}, 'avg_error': 915769.9655172414, 'total_error': 26557329},
    # }
    # # fmt: on
    print(all_solutions)

    def second_run(all_solutions):
        solution_elements = list(set([z for y in all_solutions.keys() for z in y]))

        # Skip the one with everything removed because we've handled that above.
        all_combinations = [
            y
            for x in range(len(solution_elements) + 1)
            for y in combinations(solution_elements, x)
            if y != ()
        ]

        for elements_to_remove in tqdm(all_combinations):
            print(elements_to_remove)
            foods2 = [food for food in foods if int(food[0]) not in elements_to_remove]
            solutions = solve_it(
                min_requirements,
                max_requirements,
                foods2,
                num_foods=args.n,
            )

            if solutions:
                for solution in solutions:
                    if solution not in all_solutions:
                        print(
                            "Found new solution:",
                            solution,
                            "with exclusions:",
                            elements_to_remove,
                        )

                all_solutions.update(solutions)
            else:
                print("No solutions found for", elements_to_remove)

        return all_solutions

    all_solutions = second_run(all_solutions)

    solution_elements_from_iteration = set([z for y in all_solutions.keys() for z in y])
    print(all_solutions)

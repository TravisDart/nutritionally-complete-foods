import argparse
import csv
import random
from pprint import pprint
from threading import Timer

from ortools.sat.python import cp_model

NUMBER_SCALE = 1_000  # CP-SAT only does integers, so scale to use 3 decimal places.
FOOD_OFFSET = 4  # The first 4 columns of the food data are labels.
MAX_NUMBER = 5_000_000


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(
        self,
        variables,
        nutritional_requirements,
        foods,
        error_for_quantity,
        verbose=True,
    ):
        super().__init__()
        self.__variables = variables
        self.__foods = foods
        self.__foods_by_id = {int(food[0]): food for food in foods}
        self.__nutritional_requirements = nutritional_requirements
        self.__error_for_quantity = error_for_quantity

        self.__solutions_to_keep = 10
        self.__solutions = set([])
        self.__verbose = verbose

    def get_solutions(self):
        return self.__solutions

    def on_solution_callback(self):
        food_quantity = {
            v.Name(): self.Value(v) for v in self.__variables if self.Value(v) != 0
        }

        minimal_foods = tuple(
            sorted([int(v.Name()) for v in self.__variables if self.Value(v) != 0])
        )

        # essential_solution = {
        #     int(re.search(r"\(\d+\)$", v.Name()).group(1)): self.Value(v) for v in self.__variables if self.Value(v) != 0
        # }

        nutrient_quantities = []
        for i, nutrient in enumerate(self.__nutritional_requirements):
            the_sum = sum(
                [
                    food[i + FOOD_OFFSET][0] * self.Value(self.__variables[j])
                    for j, food in enumerate(self.__foods)
                ]
            )
            nutrient_quantity = [
                nutrient[0],
                nutrient[1],
                the_sum,
                nutrient[2],
                nutrient[1][0] <= the_sum <= nutrient[2][0],  # If it's within bounds.
            ]

            nutrient_quantities += [nutrient_quantity]

        # TODO: Just record the essential solution.
        # solution = {
        #     # "essential_solution": essential_solution,
        #     "food_quantity": food_quantity,
        #     # "number_of_foods": len(food_quantity),
        #     # "nutrient_quantities": nutrient_quantities,
        #     # "avg_error": mean([self.Value(v) for v in self.__error_for_quantity]),
        #     # "total_error": sum([self.Value(v) for v in self.__error_for_quantity]),
        # }

        # # Only keep the best solutions.
        # if len(self.__solutions) >= self.__solutions_to_keep:
        #     self.__solutions.pop(0)

        # # TODO: Only keep this solution if it's new.
        if minimal_foods not in self.__solutions:
            print("Found new solution:", minimal_foods)
        self.__solutions.add(minimal_foods)


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
    nutritional_requirements,
    foods,
    num_foods: int = 4,
    should_optimize: bool = False,
    should_use_upper_value: bool = True,
    required_foods: list[int] = [],
    verbose_logging: bool = True,
):
    """
    :param should_optimize: Use the optimizing solver (initially the default; used in v0.1)
    :param nutritional_requirements: The upper and lower bounds for each nutrient.
    :param foods: A list specifying the nutritional value of each food.
    :param num_foods: Restrict the solution to only use this many foods.
    :param should_use_upper_value: Used to remove the upper bound of the nutritional requirements (for debugging)
    :param required_foods: A list of foods that must be in the solution.
    :param verbose_logging: Sets log_search_progress on the solver.
    :return: A list of solutions.
    """
    model = cp_model.CpModel()

    quantity_of_food = [
        model.NewIntVar(0, MAX_NUMBER * NUMBER_SCALE, food[2]) for food in foods
    ]

    error_for_quantity = [
        model.NewIntVar(0, MAX_NUMBER * NUMBER_SCALE, f"Error {nutrient[0]}")
        for nutrient in nutritional_requirements
    ]
    if num_foods:
        should_use_food = [model.NewIntVar(0, 1, food[0]) for food in foods]
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

    for i, nutrient in enumerate(nutritional_requirements):
        nutrient_intake = sum(
            food[i + FOOD_OFFSET][0] * solver_vars[j] for j, food in enumerate(foods)
        )
        if should_use_upper_value:
            model.AddLinearConstraint(nutrient_intake, nutrient[1][0], nutrient[2][0])
        else:
            model.Add(nutrient_intake >= nutrient[1][0])
        # Here we apply the traditional metric for error using absolute value:
        model.AddAbsEquality(
            target=error_for_quantity[i], expr=nutrient_intake - nutrient[1][0]
        )
        # Supposedly you don't need abs. I guess because the two expressions are always positive
        # model.Add(error_for_quantity[i] == nutrient_intake - nutrient[1][0])

    if should_optimize:
        model.Minimize(sum(error_for_quantity))

    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = verbose_logging
    solver.parameters.enumerate_all_solutions = True
    # The solution printer displays the nutrient that is out of bounds.
    solution_printer = VarArraySolutionPrinter(
        solver_vars, nutritional_requirements, foods, error_for_quantity
    )

    status = solver.Solve(model, solution_printer)
    print_info(status, solver, solution_printer)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        solutions = solution_printer.get_solutions()
        pprint(solutions)
        return solutions


def validate_data(nutrients, foods, food_header):
    # Make sure the labels match.
    for i, nutrient in enumerate(nutrients):
        if nutrient[0] != food_header[i + FOOD_OFFSET]:
            print(nutrient[0], "and", food_header[i + FOOD_OFFSET], "don't match")

    # Make sure the units are the same
    for i, nutrient in enumerate(nutrients):
        # Make sure the Nutritional Requirement row is consistent with itself.
        values = set()
        if nutrient[1][1] is not None:
            values.add(nutrient[1][1])
        if nutrient[2][1] is not None:
            values.add(nutrient[2][1])
        if nutrient[3] is not None:
            values.add(nutrient[3])
        if len(values) != 1:
            print("Problem!", nutrient)

        # Make sure the Nutritional Requirement unit is the same as all of the food units.
        for j, food in enumerate(foods):
            if food[i + FOOD_OFFSET][0] != 0:
                if nutrient[3] != food[i + FOOD_OFFSET][1]:
                    print(
                        "Another Problem!",
                        nutrient[3],
                        food[i + FOOD_OFFSET][1],
                        nutrient,
                        food[i + FOOD_OFFSET],
                        food[:FOOD_OFFSET],
                    )

    print("Data validated!")


def load_test_data():
    nutrients = [
        ["Vitamin A", (1, "mg"), (2, "mg")],
        ["Vitamin B", (1, "mg"), (2, "mg")],
        ["Vitamin C", (1, "mg"), (2, "mg")],
    ]

    # Each nutritional value for each food
    foods = [  #                           Vitamins A  B  C
        ["ID", "Food A", "Food", "Scientific_Name", (1, "mg"), (0, "mg"), (0, "mg")],
        ["ID", "Food B", "Food", "Scientific_Name", (0, "mg"), (1, "mg"), (0, "mg")],
        ["ID", "Food C", "Food", "Scientific_Name", (0, "mg"), (0, "mg"), (1, "mg")],
    ]

    return nutrients, foods


def load_real_data():
    # Nutrient requirements.
    nutrients = []
    with open("../data/Daily Recommended Values.csv") as csvfile:
        csvwreader = csv.reader(csvfile)
        next(csvwreader)  # Skip the header
        for row in csvwreader:
            parsed_row = [
                row[0],
                (
                    int(float(row[1].split(" ")[0]) * NUMBER_SCALE) if row[1] else 0,
                    row[1].split(" ")[1] if len(row[1].split(" ")) > 1 else None,
                ),
                (
                    int(float(row[2].split(" ")[0]) * NUMBER_SCALE)
                    if row[2]
                    else MAX_NUMBER * NUMBER_SCALE,
                    row[2].split(" ")[1] if len(row[2].split(" ")) > 1 else None,
                ),
                row[3],
            ]
            if parsed_row[2] is not None:
                try:
                    assert parsed_row[1] < parsed_row[2]
                except AssertionError as e:
                    print(parsed_row)
                    raise
            nutrients += [parsed_row]

    # Food nutrition information
    foods = []
    with open("../data/food_data.csv") as csvfile:
        # creating a csv writer object
        csvwreader = csv.reader(csvfile)
        food_header = next(csvwreader)
        for row in csvwreader:
            # This is actually not necessary, as the input file is in the correct format already.
            parsed_row = [
                *row[:4],
                *[
                    (
                        int(float(x.split(" ")[0]) * NUMBER_SCALE),
                        x.split(" ")[1] if len(x.split(" ")) > 1 else None,
                    )
                    for x in row[4:]
                ],
            ]
            foods += [parsed_row]

    validate_data(nutrients, foods, food_header)
    return nutrients, foods


def load_subset_of_data():
    nutrients, foods = load_real_data()
    foods_subset = [
        f
        for f in foods
        if f[0] in ("9024", "14091", "14355", "11672")
    ]

    # Add 10 other random foods to the list. - But add the same 10 items with each invocation of this function.
    num_additional_items = 10
    random.seed(1)
    foods_subset += random.sample(foods, num_additional_items)
    random.seed()  # Clean up after ourselves and re-seed the random number generator.

    return nutrients, foods_subset

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find sets of foods that combine to satisfy one's daily nutritional requirements."
    )
    parser.add_argument(
        "-n",
        type=int,
        default=4,
        help="The number of foods in the solution set. The default is 4 foods.",
    )
    parser.add_argument(
        "--optimize",
        action="store_true",
        default=False,
        help="Uses the optimizing solver (initially the default; used in v0.1)",
    )
    args = parser.parse_args()

    # nutrients, foods = load_test_data()
    # nutrients, foods = load_real_data()
    nutrients, foods = load_subset_of_data()

    # # Exclude foods. These were in previous solutions, but I don't want
    # # to every grow/make them, so exclude them.
    # exclude = [
    #     14091,  # Beverages, almond milk, unsweetened, shelf stable
    #     14355,  # Beverages, tea, black, brewed, prepared with tap water
    #     11656,  # Corn pudding, home prepared
    # ]
    # foods = [food for food in foods if int(food[0]) not in exclude]

    solutions = solve_it(
        nutrients, foods, num_foods=args.n, should_optimize=args.optimize
    )

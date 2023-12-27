import csv, sys
from pprint import pprint
from statistics import mean

from ortools.sat.python import cp_model

NUMBER_SCALE = 1_000  # CP-SAT only does integers, so scale to use 3 decimal places.
FOOD_OFFSET = 4  # The first 4 columns of the food data are labels.
MAX_NUMBER = 5_000_000_000


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(
        self,
        variables,
        nutritional_requirements,
        foods,
        error_for_quantity=None,
        verbose=True,
    ):
        super().__init__()
        self.__variables = variables
        self.__foods = foods
        self.__nutritional_requirements = nutritional_requirements
        self.__error_for_quantity = error_for_quantity

        self.__solutions_to_keep = 10
        self.__solutions = []
        self.__verbose = verbose

    def get_solutions(self):
        return self.__solutions

    def on_solution_callback(self):
        food_quantity = {
            v.Name(): self.Value(v) for v in self.__variables if self.Value(v) != 0
        }

        food_names = {f[0]: f[2] for f in self.__foods if f[0] in food_quantity.keys()}

        nutrient_quantities = []
        for i, nutrient in enumerate(self.__nutritional_requirements):
            the_sum = sum(
                [
                    food[i + FOOD_OFFSET][0] * self.Value(self.__variables[j])
                    for j, food in enumerate(self.__foods)
                ]
            )
            max_value = nutrient[2][0] if nutrient[2][0] else MAX_NUMBER
            nutrient_quantity = [
                nutrient[0],
                nutrient[1],
                the_sum,
                nutrient[2],
                nutrient[1][0] <= the_sum <= max_value,  # If it's within bounds.
            ]

            nutrient_quantities += [nutrient_quantity]

        solution = {
            "food_quantity": food_quantity,
            "food_names": food_names,
            "number_of_foods": len(food_quantity),
            "nutrient_quantities": nutrient_quantities,
        }

        if self.__error_for_quantity is not None:
            values = [self.Value(v) for v in self.__error_for_quantity]
            solution["avg_error"] = mean(values)
            solution["total_error"] = sum(values)

        # Only keep the best solutions.
        # if len(self.__solutions) >= self.__solutions_to_keep:
        #     self.__solutions.pop(0)

        self.__solutions += [solution]


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
    max_number_of_foods: int = 4,
    required_foods: list[int] = [],
    verbose_logging: bool = True,
    find_optimal_solution: bool = False,
):
    """
    :param nutritional_requirements: The upper and lower bounds for each nutrient.
    :param foods: A list specifying the nutritional value of each food.
    :param max_number_of_foods: If present, restrict the solution to only use this many foods.
    :param required_foods: A list of foods that must be in the solution.
    :param verbose_logging: Sets log_search_progress on the solver.
    :return: A list of solutions.
    """
    model = cp_model.CpModel()

    quantity_of_food = [model.NewIntVar(0, MAX_NUMBER, food[0]) for food in foods]
    should_use_food = [model.NewIntVar(0, 1, food[0]) for food in foods]
    solver_vars = [model.NewIntVar(0, MAX_NUMBER, food[0]) for food in foods]

    for j in range(len(foods)):
        model.AddMultiplicationEquality(
            solver_vars[j], quantity_of_food[j], should_use_food[j]
        )

    for k in required_foods:
        model.Add(should_use_food[k] == 1)

    model.Add(sum(should_use_food) == max_number_of_foods)

    if find_optimal_solution:
        error_for_quantity = [
            model.NewIntVar(0, MAX_NUMBER, f"Error {nutritional_requirement[0]}")
            for nutritional_requirement in nutritional_requirements
        ]

    for i, nutrient in enumerate(nutritional_requirements):
        nutrient_intake = sum(
            food[i + FOOD_OFFSET][0] * solver_vars[j] for j, food in enumerate(foods)
        )

        if nutrient[2][0]:  # If this nutrient has an upper bound
            model.AddLinearConstraint(nutrient_intake, nutrient[1][0], nutrient[2][0])
        else:
            model.Add(nutrient_intake >= nutrient[1][0])

        if find_optimal_solution:
            # Here we apply the traditional metric for error using absolute value:
            model.AddAbsEquality(
                target=error_for_quantity[i], expr=nutrient_intake - nutrient[1][0]
            )
            # Supposedly you don't need abs. I guess because the two expressions are always positive
            # model.Add(error_for_quantity[i] == nutrient_intake - nutrient[1][0])

    if find_optimal_solution:
        model.Minimize(sum(error_for_quantity))

    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = verbose_logging
    # The solution printer displays the nutrient that is out of bounds.
    solution_printer = VarArraySolutionPrinter(
        solver_vars, nutritional_requirements, foods, None
    )

    status = solver.Solve(model, solution_printer)
    print_info(status, solver, solution_printer)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        solutions = solution_printer.get_solutions()
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
    with open("Daily Recommended Values.csv") as csvfile:
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
                    int(float(row[2].split(" ")[0]) * NUMBER_SCALE) if row[2] else None,
                    row[2].split(" ")[1] if len(row[2].split(" ")) > 1 else None,
                ),
                row[3],
            ]
            if parsed_row[2][0] is not None:
                try:
                    assert parsed_row[1] < parsed_row[2]
                except AssertionError as e:
                    print(parsed_row)
                    raise
            nutrients += [parsed_row]

    # Food nutrition information
    foods = []
    with open("Foods.csv") as csvfile:
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


def get_bool_from_command_line():
    if len(sys.argv) > 1:
        return sys.argv[1] == "optimal"
    else:
        return False


if __name__ == "__main__":
    # nutrients, foods = load_test_data()
    nutrients, foods = load_real_data()

    solutions = solve_it(nutrients, foods, find_optimal_solution=get_bool_from_command_line())

    print("Solution: A dictionary of foods (by ID) and amounts (in grams).")
    concise_solutions = [solution["food_quantity"] for solution in solutions]
    pprint(concise_solutions)

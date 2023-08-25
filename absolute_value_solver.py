from ortools.sat.python import cp_model
import csv, math
from statistics import mean
from threading import Timer
from pprint import pprint

NUMBER_SCALE = 1_000  # CP-SAT only does integers, so scale to use 3 decimal places.
FOOD_OFFSET = 4  # The first 4 columns of the food data are labels.
MAX_NUMBER = 5000000 


class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables, nutritional_requirements, foods):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__nutritional_requirements = nutritional_requirements
        self.__foods = foods

    def on_solution_callback(self):
        for i, nutrient in enumerate(self.__nutritional_requirements):
            the_sum = sum(
                [
                    food[i + FOOD_OFFSET][0] * self.Value(self.__variables[i])
                    for food in self.__foods
                ]
            )
            if the_sum > nutrient[2][0]:  # If a nutrient is greater than the max value.
                nutrient_quantity = [
                    nutrient[0],
                    nutrient[1][0],
                    the_sum,
                    nutrient[2][0],
                ]
                print(
                    f"A solution has been found, but the value for the nutrient {nutrient[0]} is too large. "
                    f"It should be between {nutrient[1][0]} and {nutrient[2][0]}, but it's {the_sum}."
                )


def solve_it(nutritional_requirements, foods):
    model = cp_model.CpModel()

    quantity_of_food = [
        model.NewIntVar(0, MAX_NUMBER * NUMBER_SCALE, food[2]) for food in foods
    ]
    error_for_quantity = [
        model.NewIntVar(0, MAX_NUMBER * NUMBER_SCALE, f"Abs {food[2]}") for food in foods
    ]

    for i, nutrient in enumerate(nutritional_requirements):
        # I thought perhaps if the first variable was problematic, we could just make it
        # unbounded, but the solver still says the problem is Infeasible.
        # if i == 0:
        #     # Remove the upper bound constraint:
        #     model.Add(
        #         sum([food[i + FOOD_OFFSET][0] * quantity_of_food[j] for j, food in enumerate(foods)]) > nutrient[1][0]
        #     )
        # else:
        #     model.AddLinearConstraint(
        #         sum([food[i + FOOD_OFFSET][0] * quantity_of_food[j] for j, food in enumerate(foods)]),
        #         nutrient[1][0],
        #         nutrient[2][0],
        #     )

        model.Add(
            sum([food[i + FOOD_OFFSET][0] * quantity_of_food[j] for j, food in enumerate(foods)]) > nutrient[1][0]
        )
        model.AddAbsEquality(
            target=error_for_quantity[i],
            expr=sum([food[i + FOOD_OFFSET][0] * quantity_of_food[j] for j, food in enumerate(foods)]) - nutrient[1][0],
        )

    model.Minimize(sum(error_for_quantity))

    solver = cp_model.CpSolver()
    # The solution printer displays the nutrient that is out of bounds.
    solution_printer = VarArraySolutionPrinter(quantity_of_food, nutritional_requirements, foods)

    status = solver.Solve(model, solution_printer)
    outcomes = [
        "UNKNOWN",
        "MODEL_INVALID",
        "FEASIBLE",
        "INFEASIBLE",
        "OPTIMAL",
    ]
    print(outcomes[status])

def test_data():
    nutritional_requirements = [
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

    solve_it(nutritional_requirements, foods)


def real_data():
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
                    int(float(row[2].split(" ")[0]) * NUMBER_SCALE) if row[2] else MAX_NUMBER * NUMBER_SCALE,
                    row[2].split(" ")[1] if len(row[2].split(" ")) > 1 else None,
                ),
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

    solve_it(nutrients, foods)


if __name__ == "__main__":
    # test_data()
    real_data()

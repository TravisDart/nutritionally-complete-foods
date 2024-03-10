import csv
import random
from constants import NUMBER_SCALE, MAX_NUMBER


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


def non_optimizing_test_data():
    nutrients = [
        ["Vitamin A", (1, "mg"), (10, "mg")],
        ["Vitamin B", (1, "mg"), (10, "mg")],
        ["Vitamin C", (1, "mg"), (10, "mg")],
    ]

    # Each nutritional value for each food
    foods = [  #                           Vitamins A           B          C
        ["ID", "Food A", "Food", "Scientific_Name", (1, "mg"), (0, "mg"), (0, "mg")],
        ["ID", "Food B", "Food", "Scientific_Name", (0, "mg"), (1, "mg"), (0, "mg")],
        ["ID", "Food C", "Food", "Scientific_Name", (0, "mg"), (0, "mg"), (1, "mg")],
    ]

    return nutrients, foods


def load_requirements():
    # Nutrient requirements.
    nutrients = []
    min_requirements = []
    max_requirements = []
    with open("../data/Daily Recommended Values.csv") as csvfile:
        csvwreader = csv.reader(csvfile)
        next(csvwreader)  # Skip the header
        for row in csvwreader:
            min_requirement = (
                int(float(row[1].split(" ")[0]) * NUMBER_SCALE) if row[1] else 0
            )
            max_requirement = (
                int(float(row[2].split(" ")[0]) * NUMBER_SCALE)
                if row[2]
                else MAX_NUMBER * NUMBER_SCALE
            )
            min_requirements += [min_requirement]
            max_requirements += [max_requirement]
            parsed_row = [
                row[0],
                (
                    min_requirement,
                    row[1].split(" ")[1] if len(row[1].split(" ")) > 1 else None,
                ),
                (
                    max_requirement,
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

    return min_requirements, max_requirements, nutrients


def load_real_data():
    foods = []
    with open("../data/food_data.csv") as csvfile:
        # creating a csv writer object
        csvwreader = csv.reader(csvfile)
        food_labels = next(csvwreader)
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

    return foods, food_labels


def load_subset_of_data():
    foods, food_labels = load_real_data()

    # Load a known solution
    foods_subset = [f for f in foods if f[0] in ("9024", "14091", "14355", "11672")]

    # Add 10 other random foods to the list. - But add the same 10 items with each invocation of this function.
    num_additional_items = 10
    random.seed(1)
    foods_subset += random.sample(foods, num_additional_items)
    random.seed()  # Clean up after ourselves and re-seed the random number generator.

    return foods_subset, food_labels

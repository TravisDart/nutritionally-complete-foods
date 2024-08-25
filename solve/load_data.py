import csv
import random
from typing import List

from constants import NUMBER_SCALE, MAX_NUMBER
from validate_input import validate_data


def load_test_data(food_set: int = 0):
    # This is similar to the format of the CSV data.
    nutrients = [
        ["Vitamin A", (1, "mg"), (10, "mg")],
        ["Vitamin B", (1, "mg"), (10, "mg")],
        ["Vitamin C", (1, "mg"), (10, "mg")],
    ]

    food_labels = [
        "ID",
        "Category",
        "Food",
        "Scientific_Name",
        "Vitamin A",
        "Vitamin B",
        "Vitamin C",
    ]

    food_sets = [
        [  # Square                             Vitamins  A          B          C
            [1, "Food A", "Food", "Scientific_Name", (1, "mg"), (0, "mg"), (0, "mg")],
            [2, "Food B", "Food", "Scientific_Name", (0, "mg"), (1, "mg"), (0, "mg")],
            [3, "Food C", "Food", "Scientific_Name", (0, "mg"), (0, "mg"), (1, "mg")],
        ],
        [  # Non-square                        Vitamins  A          B          C
            [1, "Food A", "Food", "Scientific_Name", (1, "mg"), (0, "mg"), (0, "mg")],
            [2, "Food B", "Food", "Scientific_Name", (0, "mg"), (1, "mg"), (1, "mg")],
        ],
        [  # Sort-of simulate floats            Vitamins  A           B          C
            [1, "Food A", "Food", "Scientific_Name", (10, "mg"), (5, "mg"), (0, "mg")],
            [2, "Food B", "Food", "Scientific_Name", (0, "mg"), (5, "mg"), (10, "mg")],
        ],
    ]

    foods = food_sets[food_set]

    # This is how the data is parsed and used.
    min_requirements = [n[1][0] for n in nutrients]
    max_requirements = [n[2][0] for n in nutrients]

    return nutrients, foods, food_labels, min_requirements, max_requirements


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
                int(row[0]),
                *row[1:4],
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


def load_subset_of_data(ids: list[int] = None, random_ids: int = 0):
    if ids is None:
        ids = (2009, 4531, 9520, 11998, 14412, 20129, 31020)

    foods, food_labels = load_real_data()

    # Filter the foods to only include the ones with the specified IDs.
    foods_subset_dict = {f[0]: f for f in foods if f[0] in ids}
    # Create a list where ordering matters.
    foods_subset = []
    for id in ids:
        foods_subset += [foods_subset_dict[id]]

    # Add additional random foods to the list. - But add the same random items with each invocation of this function.
    if random_ids:
        random.seed(1)
        foods_subset += random.sample(foods, random_ids)
        random.seed()  # Clean up after ourselves and re-seed the random number generator.

    return foods_subset, food_labels


def load_data(should_use_test_data: bool = False, exclude: List[int] = None):
    if should_use_test_data:
        (
            nutrients,
            foods,
            food_labels,
            min_requirements,
            max_requirements,
        ) = load_test_data()
    else:
        foods, food_labels = load_real_data()
        # foods, food_labels = load_subset_of_data()
        min_requirements, max_requirements, nutrients = load_requirements()
        validate_data(nutrients, foods, food_labels)

    # This is a list of food IDs to exclude. This is useful to temporarily exclude a food,
    # for instance to tweak the solver so it won't return foods you don't like.
    # For a more permanent exclusion, remove the food from data/selected_foods.txt.
    # The foods below are examples that have already been excluded.
    if exclude is None:
        exclude = [
            # 35182,  # Acorn stew (Apache)
            # 14091,  # Beverages, almond milk, unsweetened, shelf stable
            # 14639,  # Beverages, rice milk, unsweetened
            # 11656,  # Corn pudding, home prepared
            # 11672,  # Potato pancakes
        ]
    if exclude:
        foods = [food for food in foods if int(food[0]) not in exclude]

    return nutrients, foods, food_labels, min_requirements, max_requirements

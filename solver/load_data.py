import csv

from constants import (
    NUMBER_SCALE,
    FOOD_OFFSET,
    NUTRIENT_UNITS,
    NUTRIENT_NAMES,
)
from .find_max import find_food_max_value


def load_test_data(food_set: int = 0):
    # This is similar to the format of the CSV data.
    nutrients = [
        ["Vitamin A", 1, 10],
        ["Vitamin B", 1, 10],
        ["Vitamin C", 1, 10],
    ]

    food_sets = [
        [  # Square        Vitamins  A  B  C
            [1, "Category > Food A", 1, 0, 0],
            [2, "Category > Food B", 0, 1, 0],
            [3, "Category > Food C", 0, 0, 1],
        ],
        [  # Non-square              A  B  C
            [1, "Category > Food A", 1, 0, 0],
            [2, "Category > Food B", 0, 1, 1],
        ],
        [  # Simulate floats          A  B  C
            [1, "Category > Food A", 10, 5, 0],
            [2, "Category > Food B", 0, 5, 10],
        ],
    ]

    expected_max_foods = [
        [10, 10, 10],
        [10, 10],
        [1, 1],
    ]

    expected_max_error = [
        [9, 9, 9],
        [9, 9, 9],
        [9, 9, 9],
    ]

    foods = food_sets[food_set]
    min_requirements = [n[1] for n in nutrients]
    max_requirements = [n[2] for n in nutrients]

    return (
        foods,
        min_requirements,
        max_requirements,
        expected_max_foods[food_set],
        expected_max_error[food_set],
    )


def load_requirements():
    with open("./data/Daily Recommended Values.csv") as csvfile:
        csvwreader = csv.reader(csvfile)
        next(csvwreader)  # Skip the header
        rows = [row for row in csvwreader]

        nutrient_names = [row[0] for row in rows]
        min_requirements = [int(float(row[1]) * NUMBER_SCALE) for row in rows]
        max_requirements = [int(float(row[2]) * NUMBER_SCALE) for row in rows]
        nutrient_units = [row[3] for row in rows]

        assert nutrient_names == NUTRIENT_NAMES
        assert nutrient_units == NUTRIENT_UNITS
        assert tuple(min_requirements) < tuple(max_requirements)

    return min_requirements, max_requirements


def load_real_data(only_these_ids: list[int] = None, exclude_ids: list[int] = None):
    foods = []
    with open("./data/food_data.csv") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header
        next(csvreader)  # Skip nutrient units
        for row in csvreader:
            parsed_row = [
                int(row[0]),  # Food ID
                row[1],  # Label
                *[int(float(x) * NUMBER_SCALE) for x in row[FOOD_OFFSET:]],
            ]
            foods += [parsed_row]

    if only_these_ids or exclude_ids:
        foods = [
            f
            for f in foods
            if (only_these_ids and f[0] in only_these_ids)
            or (exclude_ids and f[0] not in exclude_ids)
        ]

    # Make sure the foods are sorted by ID.
    foods = sorted(foods, key=lambda x: x[0])

    return foods


def load_data(
    only_these_ids: list[int] = None,
    exclude_ids: list[int] = None,
):
    """
    Load the complete data set by default, or a selection defined by only_these_ids or exclude_ids.

    # For example, this is a list of food IDs to exclude. This is useful to temporarily exclude a food,
    # for instance to tweak the solver so it won't return foods you don't like.
    # For a more permanent exclusion, remove the food from data/selected_foods.txt.
    # The foods below are examples that have already been excluded.
    exclude_ids = [
        # 35182,  # Acorn stew (Apache)
        # 14091,  # Beverages, almond milk, unsweetened, shelf stable
        # 14639,  # Beverages, rice milk, unsweetened
        # 11656,  # Corn pudding, home prepared
        # 11672,  # Potato pancakes
    ]

    only_these_ids is formatted in a similar manner.
    """
    foods = load_real_data(only_these_ids, exclude_ids)
    min_requirements, max_requirements = load_requirements()
    max_foods = find_food_max_value(foods, max_requirements)
    return foods, max_foods, min_requirements, max_requirements

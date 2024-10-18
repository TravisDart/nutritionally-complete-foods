import csv
import sqlite3
from typing import List

from constants import NUMBER_SCALE, SQL_COLUMNS, FOOD_OFFSET, NUTRIENT_UNITS


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
        [  # Non-square             Vitamins A  B  C
            [1, "Category > Food A", "Food", 1, 0, 0],
            [2, "Category > Food B", "Food", 0, 1, 1],
        ],
        [  # Simulate floats        Vitamins  A  B   C
            [1, "Category > Food A", "Food", 10, 5, 0],
            [2, "Category > Food B", "Food", 0, 5, 10],
        ],
    ]

    foods = food_sets[food_set]

    # This is how the data is parsed and used.
    min_requirements = [n[1] for n in nutrients]
    max_requirements = [n[2] for n in nutrients]

    return nutrients, min_requirements, max_requirements


def load_requirements():
    with open("../data/Daily Recommended Values.csv") as csvfile:
        csvwreader = csv.reader(csvfile)
        next(csvwreader)  # Skip the header
        rows = [row for row in csvwreader]

        nutrient_names = [row[0] for row in rows]
        min_requirements = [int(float(row[1]) * NUMBER_SCALE) for row in rows]
        max_requirements = [int(float(row[2]) * NUMBER_SCALE) for row in rows]
        nutrient_units = [row[3] for row in rows]

        assert nutrient_names == SQL_COLUMNS[FOOD_OFFSET:]
        print("nutrient_units", nutrient_units, NUTRIENT_UNITS)
        assert nutrient_units == NUTRIENT_UNITS
        assert tuple(min_requirements) < tuple(max_requirements)

    return min_requirements, max_requirements


def load_real_data(only_these_ids: list[int] = None, exclude_ids: list[int] = None):
    con = sqlite3.connect("../data/food.sqlite")
    cur = con.cursor()
    query = "SELECT * FROM food"
    if only_these_ids:
        query += " WHERE id IN ({})".format(",".join(only_these_ids))

    if only_these_ids and exclude_ids:
        query += " AND "
    elif exclude_ids:
        query += " WHERE "

    if exclude_ids:
        query += "id NOT IN ({})".format(",".join(exclude_ids))

    print("Query:", query)
    cur.execute(query)
    rows = cur.fetchall()
    return rows


def load_data(
    should_use_test_data: bool = False,
    only_these_ids: list[int] = None,
    exclude_ids: list[int] = None,
):
    if should_use_test_data:
        foods, min_requirements, max_requirements = load_test_data()
    else:
        foods = load_real_data(only_these_ids, exclude_ids)
        min_requirements, max_requirements = load_requirements()

    return foods, min_requirements, max_requirements

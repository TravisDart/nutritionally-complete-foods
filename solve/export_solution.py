from pprint import pprint
from typing import Optional

from load_data import load_real_data


def export_food_data(selected_food_ids: Optional[list[int]]):
    foods, _ = load_real_data()
    if selected_food_ids:
        selected_foods = [food for food in foods if int(food[0]) in selected_food_ids]
        return selected_foods
    else:
        return foods


if __name__ == "__main__":
    pprint(export_food_data([9024, 14091, 14355, 11672]))

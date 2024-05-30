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
    pprint(export_food_data([9089, 9412, 11656, 11946, 14091, 14412, 14355]))

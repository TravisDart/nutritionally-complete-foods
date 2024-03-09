from load_data import load_real_data
from typing import List


def export_solution(selected_food_ids: list[int]):
    _, foods = load_real_data()
    selected_foods = [food for food in foods if int(food[0]) in selected_food_ids]
    return selected_foods

    print(nutrients)
    print(foods)


if __name__ == "__main__":
    print(export_solution([9024, 14091, 14355, 11672]))

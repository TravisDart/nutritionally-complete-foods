from pprint import pprint

from load_data import load_real_data


def export_solution(selected_food_ids: list[int]):
    foods, _ = load_real_data()
    selected_foods = [food for food in foods if int(food[0]) in selected_food_ids]
    return selected_foods


if __name__ == "__main__":
    pprint(export_solution([9024, 14091, 14355, 11672]))

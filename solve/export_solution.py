from typing import Optional
from utils import dict_to_ordered_tuples
from download_data import load_real_data, load_subset_of_data, load_requirements
from solve import solve_it
from constants import KNOWN_SOLUTIONS


def export_food_data(selected_food_ids: Optional[list[int]]):
    foods, _ = load_real_data()
    if selected_food_ids:
        selected_foods = [food for food in foods if int(food[0]) in selected_food_ids]
        return selected_foods
    else:
        return foods


def convert_to_dict(foods):
    foods_dict = {}
    for food in foods:
        foods_dict[food[0]] = food
    return foods_dict


def pretty_output(solution):
    for food_id, qty in solution:
        food_name = foods_dict[food_id][2]
        print(food_name, f"({qty:,}g)", f"- ID #{food_id}")


def output_for_notebook(i, solution):
    print(f"Solution {i + 1}:")
    for food_id, qty in solution:
        food_name = foods_dict[food_id][2]
        print(f"{food_name} ({qty:,}g) - ID #{food_id}")


if __name__ == "__main__":
    # Don't output solutions containing these foods.
    exclude = [
        # For example:
        # 9436,  # Mango nectar, canned
        # 35092,  # Willow, leaves in oil (Alaska Native)
        # 48052,  # Vital wheat gluten
        # 12156,  # Nuts, walnuts, glazed
        # 9195,  # Olives, pickled, canned or bottled, green
        # 43449,  # Beans, baked, canned, no salt added
        4531,  # Oil, soybean lecithin
        # 42231,  # Oil, flaxseed, cold pressed
        # 4707,  # Oil, flaxseed, contains added sliced flaxseed
        # 4588,  # Oil, oat
        # 9328,  # Maraschino cherries, canned, drained
        # 4038,  # Oil, wheat germ
        # 4513,  # Vegetable oil, palm kernel
        # 4581,  # Oil, avocado
        # 35092,  # Willow, leaves in oil(Alaska Native)
        16112,  # Miso
        # All solutions contain one of these types of seaweed, so we can't exclude those.
        # 31020,  # Seaweed, Canadian Cultivated EMI - TSUNOMATA, rehydrated
        # 31019,  # Seaweed, Canadian Cultivated EMI - TSUNOMATA, dry
    ]

    min_requirements, max_requirements, _ = load_requirements()
    foods, _ = load_real_data()
    foods_dict = convert_to_dict(foods)

    # solutions = KNOWN_SOLUTIONS[num_foods] if num_foods else KNOWN_SOLUTIONS

    for num_foods in [7]:  # KNOWN_SOLUTIONS:
        print("=" * 100)
        print(f"{num_foods}-food Solutions")
        print("=" * 100)

        used_foods = {}
        for i, solution in enumerate(KNOWN_SOLUTIONS[num_foods]):
            if exclude:
                if any(food_id in exclude for food_id, _ in solution):
                    continue

            pretty_output(solution)

            print()

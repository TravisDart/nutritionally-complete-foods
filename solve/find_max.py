import math
from typing import List

from constants import FOOD_OFFSET


def find_max_x(y: List[int], z: List[int]):
    """
    Find the maximum value of x that satisfies the equation y * x <= z,

    This algorithm goes component by component and finds the "ceiling".
    There are many ways to visualize this and many algorithms to compute it.
    """
    normalized = [z[i] / y[i] for i in range(len(y)) if y[i] != 0]
    normalized.sort()
    max_x = normalized[0]
    return max_x


def find_food_max_value(foods, max_requirements):
    return [
        math.ceil(find_max_x(food[FOOD_OFFSET:], max_requirements)) for food in foods
    ]


if __name__ == "__main__":
    assert find_max_x([1, 2, 3], [12, 12, 12]) == 4.0
    assert find_max_x([1, 3, 2], [12, 12, 12]) == 4.0
    assert find_max_x([1, 3, 2], [10, 12, 14]) == 4.0
    assert find_max_x([2, 3, 4], [10, 15, 20]) == 5.0

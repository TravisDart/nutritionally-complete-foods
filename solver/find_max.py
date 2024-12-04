import math
from typing import List

from constants import FOOD_OFFSET


def find_max_x(y: List[int], z: List[int]):
    """
    Find the maximum value of x that satisfies the equation y * x <= z.

    This algorithm goes component by component and finds the "ceiling".
    There are many ways to visualize this and many algorithms to compute it.

    In our case y is the amount of the nutrient in 1 gram
    and z is the maximum value of the nutrient.
    """
    normalized = [z[i] / y[i] for i in range(len(y)) if y[i] != 0]
    normalized.sort()
    max_x = normalized[0]
    return max_x


def find_food_max_value(foods, max_requirements):
    """
    Calculate the maximum value we would ever need for each food.

    For example, we will never need more than 2,917 grams of Apples because that's when
    one of the nutrients (fiber) goes over the upper bound. One gram of apples contains .024 g of fiber,
    and 2,917 * .024 = 70.008, which is above the upper bound of 70g.
    """
    return [
        math.ceil(find_max_x(food[FOOD_OFFSET:], max_requirements)) for food in foods
    ]

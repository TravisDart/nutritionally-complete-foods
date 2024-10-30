import math

from .load_data import load_data
from constants import FOOD_OFFSET, NUMBER_SCALE


def find_top_values_in_each_column(foods, max_qty, num_values: int):
    """Finds the num_values greatest numbers in each column of a 2D list.

    Args:
      x: A 2D list of numbers. The rows are always the same number of elements,
      let's say m elements (the ~1,000+ foods) and n columns (the 29 nutrients)

        x = [
          [row1_col1, row1_col2, ... row1_coln],
          [row2_col1, row2_col2, ... row2_coln],
          ...
          [rowm_col1, rowm_col2, ... rowm_coln],
        ]

    Returns:
      A 2D list containing the num_values greatest numbers (usually 7)
      from each column.

        y = [
          [col1_val1, col1_val2, ... col1_val7],
          [col2_val1, col2_val2, ... col2_val7],
          ...
          [coln_val1, coln_val2, ... coln_val7],
        ]
    """
    max_foods = [
        [col * max_qty[i] for col in foods[i][FOOD_OFFSET:]] for i in range(len(foods))
    ]

    # Transpose the matrix.
    transposed_x = list(zip(*max_foods))

    # Sort each row in descending order
    sorted_x = [sorted(row, reverse=True) for row in transposed_x]

    # Extract the first 7 elements (or whatever) from each row
    top_values = [row[:num_values] for row in sorted_x]

    return top_values


def find_max_error(foods, max_qty, num_foods, min_requirements):
    top_n_values = find_top_values_in_each_column(foods, max_qty, num_foods)
    return [
        sum(top_n_values[i]) - min_requirements[i] for i in range(len(min_requirements))
    ]


if __name__ == "__main__":
    num_foods = 3

    x = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    top_n_values = find_top_values_in_each_column(x, num_foods)
    expected_values = [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
    assert top_n_values == expected_values

    max_error = find_max_error(top_n_values, num_foods, [1, 2, 3], NUMBER_SCALE)
    expected_max_error = [23 * NUMBER_SCALE, 13 * NUMBER_SCALE, 3 * NUMBER_SCALE]
    assert max_error == expected_max_error

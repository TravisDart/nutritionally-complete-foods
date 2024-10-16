import math

from load_data import load_data
from constants import FOOD_OFFSET, NUMBER_SCALE


def find_top_values_in_each_column(x, num_values: int):
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
    # Transpose the matrix.
    transposed_x = list(zip(*x))

    # Sort each row in descending order
    sorted_x = [sorted(row, reverse=True) for row in transposed_x]

    # Extract the first 7 elements from each row
    y = [row[:num_values] for row in sorted_x]

    return y


def find_max_error(food_values, num_foods, min_requirements, NUMBER_SCALE):
    top_n_values = find_top_values_in_each_column(food_values, num_foods)
    return [
        (sum(top_n_values[i]) - min_requirements[i]) * NUMBER_SCALE
        for i in range(len(min_requirements))
    ]


def find_least_nonzero_values_in_each_column(x):
    """
    Similar to find_top_values_in_each_column(), but finds the least non-zero values in each column.
    """
    transposed_x = list(zip(*x))
    sorted_x = [sorted([r for r in row if r != 0]) for row in transposed_x]
    y = [row[0] for row in sorted_x]
    return y


def calculate_scale():
    """
    Really, NUMBER_SCALE probably won't change, but we need to put this code somewhere.
    It doesn't help that all of our values are already multiplied by NUMBER_SCALE.
    """

    _, foods, _, min_requirements, max_requirements = load_data()
    food_values = [[f2[0] / NUMBER_SCALE for f2 in f1[FOOD_OFFSET:]] for f1 in foods]

    # Scale for foods
    minimum = find_least_nonzero_values_in_each_column(food_values)

    column_scale = [math.ceil(-math.log10(m)) for m in minimum]
    foods_scale = max(column_scale)

    min_requirements_scale = max(
        [math.ceil(-math.log10(m / NUMBER_SCALE)) for m in min_requirements]
    )
    max_requirements_scale = max(
        [math.ceil(-math.log10(m / NUMBER_SCALE)) for m in max_requirements]
    )
    scale = max(foods_scale, min_requirements_scale, max_requirements_scale)
    return 10**scale


if __name__ == "__main__":
    scale = calculate_scale()
    assert scale == NUMBER_SCALE

    num_foods = 3

    x = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    top_n_values = find_top_values_in_each_column(x, num_foods)
    expected_values = [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
    assert top_n_values == expected_values

    max_error = find_max_error(top_n_values, num_foods, [1, 2, 3], NUMBER_SCALE)
    expected_max_error = [23 * NUMBER_SCALE, 13 * NUMBER_SCALE, 3 * NUMBER_SCALE]
    assert max_error == expected_max_error

from typing import List


def find_max_x(y: List[int], z: List[int]):
    """
    Find the maximum value of x that satisfies the equation y * x <= z,

    This algorithm goes component by component and finds the "ceiling".
    There are many ways to visualize this and many algorithms to compute it.
    """
    normalized = [z[i] / y[i] for i in range(len(y))]
    normalized.sort()
    max_x = normalized[0]
    return max_x


if __name__ == "__main__":
    assert find_max_x([1, 2, 3], [12, 12, 12]) == 4.0
    assert find_max_x([1, 3, 2], [12, 12, 12]) == 4.0
    assert find_max_x([1, 3, 2], [10, 12, 14]) == 4.0
    assert find_max_x([2, 3, 4], [10, 15, 20]) == 5.0

import argparse
import numpy as np
from load_data import load_requirements


def ordered_dict_values(food_quantity: dict[str, int]):
    """Turn the dictionary into a list of values, being sure to preserve the id order of the keys."""
    return [x[1] for x in sorted(food_quantity.items(), key=lambda item: int(item[0]))]


def dict_to_ordered_tuples(food_quantity: dict[str, int]):
    """
    Turn the dictionary-formatted solution into a tuple-formatted solution,
    being sure to preserve the id order of the keys.
    """
    return [
        (int(x[0]), x[1])
        for x in sorted(food_quantity.items(), key=lambda item: int(item[0]))
    ]


def evaluate_result(solution, min_bound, max_bound, verbose=True, assert_good=False):
    error = np.linalg.norm(solution - min_bound)
    under_bounds = [solution[x] < min_bound[x] for x in range(len(max_bound))]
    under_bounds_str = "".join(["1" if x else "0" for x in under_bounds])
    over_bounds = [solution[x] > max_bound[x] for x in range(len(max_bound))]
    over_bounds_str = "".join(["1" if x else "0" for x in over_bounds])
    is_out_of_bounds = any(under_bounds) or any(over_bounds)

    if verbose:
        print("solution", solution)
        print("error", error)
        print("Components Under Bounds (Bitstring)", under_bounds_str)
        print("Components Over Bounds  (Bitstring)", over_bounds_str)
        print("is_out_of_bounds", is_out_of_bounds)

    if assert_good:
        assert not is_out_of_bounds

    return (
        error,
        under_bounds,
        over_bounds,
        is_out_of_bounds,
        under_bounds_str,
        over_bounds_str,
    )


def verify_solution(
    solution,
    verbose=False,
):
    """
    Multiply the foods' nutritional values by the quantites found by the solver
    to verify that it satisfies the constraints.
    """
    ids = [x[0] for x in solution]
    food_data, _ = load_subset_of_data(ids=ids)

    min_requirements, max_requirements, _ = load_requirements()

    just_matrix_coefficients = [[y[0] for y in x[4:]] for x in food_data]
    nutrition_matrix = np.array(just_matrix_coefficients)
    nutrition_matrix = nutrition_matrix.T

    food_quantities = [x[1] for x in solution]
    result = nutrition_matrix @ food_quantities

    evaluate_result(
        result, min_requirements, max_requirements, assert_good=True, verbose=verbose
    )


def get_arg_parser():
    parser = argparse.ArgumentParser(
        description="Find sets of foods that combine to satisfy one's daily nutritional requirements."
    )
    parser.add_argument(
        "-n",
        type=int,
        help=(
            "Only look for solutions with this number of foods."
            "The default is to sequentially look for solutions starting with 1 food."
        ),
    )
    parser.add_argument(
        "--test-data",
        action="store_true",
        help="Use test data instead of real data.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity logging. Use -vv for very verbose.",
    )
    return parser

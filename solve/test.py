import numpy as np
from load_data import load_requirements, load_subset_of_data, load_test_data, load_data
from solve import solve_it
from constants import KNOWN_SOLUTIONS
from utils import (
    ordered_dict_values,
    dict_to_ordered_tuples,
    verify_solution,
    evaluate_result,
)


def multiply_known_solutions(verbose=False):
    """Multiply out each known solution to see if it's really a solution."""

    nutrients, foods, food_labels, min_requirements, max_requirements = load_data()
    for number_of_foods in KNOWN_SOLUTIONS:
        for known_solution in KNOWN_SOLUTIONS[number_of_foods]:
            verify_solution(known_solution, verbose=verbose)


def solve_against_known_solutions(verbose=False):
    """Run the solver against just the foods in the known solutions to verify that a solution can be found."""

    min_requirements, max_requirements, _ = load_requirements()
    for number_of_foods in KNOWN_SOLUTIONS:
        for known_solution in KNOWN_SOLUTIONS[number_of_foods]:
            ids = [x[0] for x in known_solution]
            foods_in_solution, _ = load_subset_of_data(ids=ids)

            solver_result = solve_it(
                min_requirements,
                max_requirements,
                foods_in_solution,
                num_foods=len(known_solution),
                log_level=int(verbose) * 2,
            )
            assert len(solver_result) == 1  # Only one solution

            # Convert the dict-formatted solution to a tuple format. We need to make this more consistent.
            food_quantity = list(solver_result.values())[0]["food_quantity"]
            tuple_solution = dict_to_ordered_tuples(food_quantity)

            verify_solution(tuple_solution, verbose=verbose)


def trivial_tests(verbose=False):
    for food_set in range(3):
        (
            nutrients,
            example_foods,
            _,  # Food labels
            min_requirements,
            max_requirements,
        ) = load_test_data(food_set)

        solver_result = solve_it(
            min_requirements,
            max_requirements,
            example_foods,
            num_foods=len(example_foods),
            log_level=int(verbose),
        )

        just_matrix_coefficients = [[y[0] for y in x[4:]] for x in example_foods]
        A = np.array(just_matrix_coefficients)
        A = A.T

        food_quantity = list(solver_result.values())[0]["food_quantity"]
        solution = ordered_dict_values(food_quantity)

        result = A @ solution
        evaluate_result(
            result,
            min_requirements,
            max_requirements,
            verbose=verbose,
            assert_good=True,
        )
        if verbose:
            print(f"Test {food_set} passed")


if __name__ == "__main__":
    trivial_tests(verbose=False)
    multiply_known_solutions(verbose=False)
    solve_against_known_solutions(verbose=False)
    print("All assertions pass.")

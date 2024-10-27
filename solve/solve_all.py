"""
This program tries to find all combinations of foods that will meet the nutritional requirements of a person.
See README.md for a full description. In short, the ultimate goal of this project is to find all solutions.
However, it looks like we need a different solver to do this.
"""
import sys
from itertools import combinations
import functools
from tqdm import tqdm

from load_data import load_data
from solve import solve_it
from utils import get_arg_parser


def solve_it2(min_requirements, max_requirements, num_foods, foods):
    solution_data = solve_it(min_requirements, max_requirements, foods, num_foods)
    if not solution_data:
        return None, None

    # A list of tuples of ordered food IDs.
    solutions = solution_data.keys()

    # Basically just a flattend list of solutions without duplicates.
    foods_in_solutions = set(
        [food for solution in solutions.keys() for food in solution]
    )

    return foods_in_solutions, solutions


if __name__ == "__main__":
    # Keep track of these things:
    foods_in_solutions = {}
    all_solutions = {}

    # Start with the empty tuple to seed the run and start by not removing any foods.
    food_combinations_to_exclude = {()}

    # Keep track of the combinations we've tried to remove so we can recalculate our work queue.
    tried_to_solve_without = {}

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Initialize the solver function
    args = get_arg_parser().parse_args()
    nutrients, foods, food_labels, min_requirements, max_requirements = load_data(
        should_use_test_data=args.test_data
    )
    solve = functools.partial(
        solve_it2, min_requirements, max_requirements, num_foods=args.n
    )

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Loop until we've tried to solve without the combinations of elements of every solution.
    while tried_to_solve_without:
        foods_without = [
            [
                food
                for food in foods
                if int(food[0]) not in food_combinations_to_exclude.pop()
            ]
        ]
        foods_in_solutions, solution_combinations = solve(foods_without)
        if solution_combinations:
            # Update the global tally
            foods_in_solutions.update(foods_in_solutions)
            all_solutions.update(solution_combinations)

            # Recalculate all of combinations
            tried_to_solve_without = [
                y
                for x in range(len(foods_in_solutions) + 1)
                for y in combinations(foods_in_solutions, x)
                if y != tried_to_solve_without
            ]

"""
This program tries to find all combinations of foods that will meet the nutritional requirements of a person.
See README.md for a full description. In short, the ultimate goal of this project is to find all solutions.
However, it looks like we need a different solver to do this.
"""
import sys
from itertools import combinations

from tqdm import tqdm

from load_data import load_data
from solve import solve_it
from utils import get_arg_parser


if __name__ == "__main__":
    args = get_arg_parser().parse_args()
    nutrients, foods, food_labels, min_requirements, max_requirements = load_data(
        should_use_test_data=args.test_data
    )

    def first_run(min_requirements, max_requirements, foods, num_foods):
        # Find the initial set of solutions, normally.
        keep_going = True
        all_solutions = {}
        while keep_going:
            solutions = solve_it(
                min_requirements,
                max_requirements,
                foods,
                num_foods,
            )
            print("Solution:", solutions)
            if solutions:
                all_solutions.update(solutions)

                # Remove foods in the solution from the list of foods:
                for solution in dict(solutions).keys():
                    foods = [food for food in foods if int(food[0]) not in solution]
            else:
                keep_going = False

        return all_solutions

    all_solutions = first_run(
        min_requirements,
        max_requirements,
        foods,
        num_foods=args.n,
    )
    print(all_solutions)

    def second_run(all_solutions):
        solution_elements = list(set([z for y in all_solutions.keys() for z in y]))

        # Skip the one with everything removed because we've handled that above.
        all_combinations = [
            y
            for x in range(len(solution_elements) + 1)
            for y in combinations(solution_elements, x)
            if y != ()
        ]

        for elements_to_remove in tqdm(all_combinations):
            print(elements_to_remove)
            foods2 = [food for food in foods if int(food[0]) not in elements_to_remove]
            solutions = solve_it(
                min_requirements,
                max_requirements,
                foods2,
                num_foods=args.n,
            )

            if solutions:
                for solution in solutions:
                    if solution not in all_solutions:
                        print(
                            "Found new solution:",
                            solution,
                            "with exclusions:",
                            elements_to_remove,
                        )

                all_solutions.update(solutions)
            else:
                print("No solutions found for", elements_to_remove)

        return all_solutions

    all_solutions = second_run(all_solutions)

    solution_elements_from_iteration = set([z for y in all_solutions.keys() for z in y])
    print(solution_elements_from_iteration)
    print(all_solutions)

"""
This program tries to find all combinations of foods that will meet the nutritional requirements of a person.
See README.md for a full description. In short, the ultimate goal of this project is to find all solutions.
However, it looks like we need a different solver to do this.
"""
from itertools import combinations
import functools
from solve import solve_it
from solver.initialize import initialize


def solve_it2(max_foods, min_requirements, max_requirements, num_foods, verbose, foods):
    return solve_it(
        foods,
        max_foods,
        min_requirements,
        max_requirements,
        num_foods,
        log_level=verbose,
    )


if __name__ == "__main__":
    # Keep track of these things:
    foods_in_solutions = set()
    all_solutions = set()

    # We probably could restructure the algorithm to not need this, but it makes it conceptually easier.
    all_combinations = {()}

    # Start with the empty tuple to seed the run and start by not removing any foods.
    food_combinations_to_exclude = {()}

    # The combinations we've tried to remove. This will always be a subset of all_solutions.
    tried_to_solve_without = set()

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Initialize the solver function
    foods, max_foods, min_requirements, max_requirements, verbose = initialize()
    solve = functools.partial(
        solve_it2,
        max_foods,
        min_requirements,
        max_requirements,
        7,  # num_foods
        verbose,  # log_level
    )

    # For testing:
    foods_in_solutions = {11936, 11266, 14412, 9520, 16112, 11257, 12156}
    all_solutions = {(9520, 11257, 11266, 11936, 12156, 14412, 16112)}
    tried_to_solve_without = {()}
    all_combinations = set(
        [
            tuple(y)
            for x in range(len(foods_in_solutions) + 1)
            for y in combinations(foods_in_solutions, min(x, 7))
        ]
    )
    food_combinations_to_exclude = all_combinations - tried_to_solve_without

    # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # Loop until we've tried to solve without the combinations of elements of every solution.
    while food_combinations_to_exclude:
        exclusion = food_combinations_to_exclude.pop()
        print()
        print("Excluding", exclusion)
        foods_without = [food for food in foods if int(food[0]) not in exclusion]
        solution = solve(foods_without)
        tried_to_solve_without.add(exclusion)
        if solution:
            # Update the global tally
            foods_in_solutions.update(solution)
            all_solutions.add(solution)

            print("foods_in_solutions", foods_in_solutions)
            print("all_solutions", all_solutions)

            # Recalculate all of combinations
            all_combinations = set(
                [
                    tuple(y)
                    for x in range(len(foods_in_solutions) + 1)
                    for y in combinations(foods_in_solutions, min(x, 7))
                ]
            )
            # The ones we need to do are all the combinations minus the ones we've tried.
            food_combinations_to_exclude = all_combinations - tried_to_solve_without

        print("all_combinations", len(all_combinations))
        print("food_combinations_to_exclude", len(food_combinations_to_exclude))
        print("tried_to_solve_without", len(tried_to_solve_without))

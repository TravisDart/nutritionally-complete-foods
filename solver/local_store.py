from itertools import combinations


class LocalStore:
    def __init__(self, testing=False):
        # Keep track of these things:
        self.foods_in_solutions = set()
        self.all_solutions = set()

        # We probably could restructure the algorithm to not need this, but it makes it conceptually easier.
        self.all_combinations = {()}

        # Start with the empty tuple to seed the run and start by not removing any foods.
        self.food_combinations_to_exclude = {()}

        # The combinations we've tried to remove. This will always be a subset of all_solutions.
        self.tried_to_solve_without = set()

        if testing:
            self.foods_in_solutions = {11936, 11266, 14412, 9520, 16112, 11257, 12156}
            self.all_solutions = {(9520, 11257, 11266, 11936, 12156, 14412, 16112)}
            self.tried_to_solve_without = {()}
            self.all_combinations = set(
                [
                    tuple(y)
                    for x in range(len(self.foods_in_solutions) + 1)
                    for y in combinations(self.foods_in_solutions, min(x, 7))
                ]
            )
            self.food_combinations_to_exclude = (
                self.all_combinations - self.tried_to_solve_without
            )

    def exclusions(self):
        while self.food_combinations_to_exclude:
            exclusion = self.food_combinations_to_exclude.pop()
            yield exclusion

    def add_try(self, exclusion):
        self.tried_to_solve_without.add(exclusion)

    def add_solution(self, solution):
        self.foods_in_solutions.update(solution)
        self.all_solutions.add(solution)

        # Recalculate all of combinations
        self.all_combinations = set(
            [
                tuple(y)
                for x in range(len(self.foods_in_solutions) + 1)
                for y in combinations(self.foods_in_solutions, min(x, 7))
            ]
        )
        # The ones we need to do are all the combinations minus the ones we've tried.
        self.food_combinations_to_exclude = (
            self.all_combinations - self.tried_to_solve_without
        )

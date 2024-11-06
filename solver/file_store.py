from multiprocessing import Lock

from itertools import combinations


from solver.logger import Logger


class FileStore:
    def __init__(
        self,
        solution_file_name: str,
        tried_file_name: str,
        solution_lock: Lock,
        tried_lock: Lock,
        num_foods: int,
        logger: Logger,
    ):
        self.solution_file_name = solution_file_name
        self.tried_file_name = tried_file_name
        self.solution_lock = solution_lock
        self.tried_lock = tried_lock
        self.num_foods = num_foods
        self.logger = logger
        self.logger.log("Starting")

    @classmethod
    def initialize(cls, solution, solution_file_name, tried_file_name):
        try:
            with open(solution_file_name, "r+") as f:
                f.truncate(0)
                f.write(" ".join([str(e) for e in sorted(solution)]) + "\n")
        except FileNotFoundError:
            with open(solution_file_name, "w") as f:
                pass

        try:
            with open(tried_file_name, "r+") as f:
                f.truncate(0)
        except FileNotFoundError:
            with open(tried_file_name, "w") as f:
                pass

    def exclusions(self):
        self.logger.log("Checking for exclusions")
        while True:
            with self.solution_lock:
                solutions = (
                    open(self.solution_file_name, "r").read().strip().splitlines()
                )

            with self.tried_lock:
                tried_exclusions = (
                    open(self.tried_file_name, "r").read().strip().splitlines()
                )
            tried_exclusions = set(
                [tuple([int(ee) for ee in e.split()]) for e in tried_exclusions]
            )

            all_foods = set()
            for solution in solutions:
                for food in solution.split():
                    all_foods.add(int(food))

            all_combinations = set(
                [
                    tuple(y)
                    for x in range(len(all_foods) + 1)
                    for y in combinations(all_foods, min(x, self.num_foods))
                ]
            )
            untried_solutions = all_combinations - tried_exclusions
            if not untried_solutions:
                break

            self.logger.log(
                "all_foods",
                len(all_foods),
                "all_combinations",
                len(all_combinations),
                "untried_solutions",
                len(untried_solutions),
                "tried_exclusions",
                len(tried_exclusions),
            )
            return untried_solutions.pop()

        self.logger.log("No more exclusions. Exiting.")

    def add_try(self, exclusion):
        with self.tried_lock:
            with open(self.tried_file_name, "a") as f:
                f.write(" ".join([str(e) for e in sorted(exclusion)]) + "\n")

    def add_solution(self, solution):
        self.logger.log("Adding solution", solution)
        with self.solution_lock:
            with open(self.solution_file_name, "a") as f:
                f.write(" ".join([str(e) for e in sorted(solution)]) + "\n")

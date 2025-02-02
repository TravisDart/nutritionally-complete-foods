from ortools.sat.python import cp_model


class SingleSolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        super().__init__()
        self.__variables = variables
        self.__solution = None

    def get_solutions(self):
        return self.__solution

    def on_solution_callback(self):
        # Just the ordered IDs of the foods in the solution.
        self.__solution = tuple(
            sorted([int(v.Name()) for v in self.__variables if self.Value(v) != 0])
        )
        self.StopSearch()


class MultipleSolutionPrinter(cp_model.CpSolverSolutionCallback):
    def __init__(
        self,
        variables,
        log_level: int = 0,
    ):
        super().__init__()
        self.__variables = variables
        self.__solutions = {}
        self.__log_level = log_level

    def get_solutions(self):
        return self.__solutions

    def on_solution_callback(self):
        # Just the ordered IDs of the foods in the solution.
        solution_id = tuple(
            sorted([int(v.Name()) for v in self.__variables if self.Value(v) != 0])
        )

        # Info on the solution.
        solution_value = {
            "food_quantity": {
                v.Name(): self.Value(v) for v in self.__variables if self.Value(v) != 0
            },
        }
        solution_value["total_quantity"] = sum(solution_value["food_quantity"].values())

        # If we already have this combination of foods, pick the one with the lowest quantity.
        if solution_id in self.__solutions:
            if (
                solution_value["total_quantity"]
                < self.__solutions[solution_id]["total_quantity"]
            ):
                if self.__log_level >= 1:
                    print("Found more optimal solution for", solution_id)
                    print("Old solution:", self.__solutions[solution_id])
                    print("New solution:", solution_value)
                self.__solutions[solution_id] = solution_value
        else:
            self.__solutions[solution_id] = solution_value
            if self.__log_level >= 1:
                print("Found a new solution:", solution_id)


def print_info(status, solver, solution_printer):
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("\nStatistics")
        print(f"  status   : {solver.StatusName(status)}")
        print(f"  conflicts: {solver.NumConflicts()}")
        print(f"  branches : {solver.NumBranches()}")
        print(f"  wall time: {solver.WallTime()} s")
        print(f"  sol found: {len(solution_printer.get_solutions())}")
    # I'm pretty sure this used to work...
    # elif status == cp_model.MODEL_INVALID:
    #     print(cp_model.Validate())
    else:
        outcomes = [
            "UNKNOWN",
            "MODEL_INVALID",
            "FEASIBLE",
            "INFEASIBLE",
            "OPTIMAL",
        ]
        outcome = outcomes[status]
        print(outcome)

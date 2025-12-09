from A_star_Weighted_A_star.a_star_solver import AStarSolver
from CSP_AC3.csp_solver import CSPSolver
from Controller.data_checking import DataChecker
from HillClimbingSA.hill_climbing_sa import HillClimbSolver
import concurrent.futures


class PuzzleManager:
    def __init__(self, data:dict, algorithm:str):
        self.__data = data
        self.__algorithm = algorithm

    def run(self):
        valid_result = self.__validate()
        if valid_result is not None:
            error = valid_result[1] if isinstance(valid_result, tuple) else None
            if error:
                return None, error

        return self.__route()

    def __validate(self):
        try:
            checker = DataChecker(self.__data)
            if not checker.general_check():
                return None, "Invalid puzzle: clues are inconsistent or out of range"
        except ValueError as e:
            return None, str(e)


    def __route(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:

            future = executor.submit(self.__run_algorithm)

            try:
                result, metrics = future.result(timeout=180)
                return result, metrics

            except concurrent.futures.TimeoutError:
                return None, {"error": "Timeout after 600 seconds"}

    def __run_algorithm(self):
        if self.__algorithm == "CSP":
            return CSPSolver.solve(self.__data)

        if self.__algorithm == "A*":
            solver = AStarSolver(self.__data)
            return solver.solve()

        if self.__algorithm == "HillClimb":
            return HillClimbSolver.solve(self.__data)

        return None, {"error": "Unknown algorithm"}

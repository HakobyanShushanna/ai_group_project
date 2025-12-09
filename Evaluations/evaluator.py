from CluesGenerator.clues_generator import RandomPuzzleGenerator
from Controller.puzzle_manager import PuzzleManager
from statistics import mean, stdev
import multiprocessing as mp

def _isolated_run(data, algorithm, return_dict):
    try:
        manager = PuzzleManager(data, algorithm)
        result, metrics = manager.run()
        return_dict["result"] = result
        return_dict["metrics"] = metrics
    except Exception as e:
        return_dict["error"] = str(e)


class Evaluator:
    def __init__(self, n: int, threshold: float):
        self.__n = n
        self.__threshold = threshold

        self.__csp_time = []
        self.__a_star_time = []
        self.__hill_time = []

        self.__csp_done = False
        self.__a_star_done = False
        self.__hill_done = False

        self.__fail_counts = {
            "CSP": 0,
            "A*": 0,
            "HillClimb": 0
        }

    def __run_with_isolation(self, data, algorithm, timeout_sec=180):
        manager = mp.Manager()
        return_dict = manager.dict()

        p = mp.Process(target=_isolated_run, args=(data, algorithm, return_dict))
        p.start()
        p.join(timeout_sec)

        if p.is_alive():
            print(f"[TIMEOUT] {algorithm} exceeded {timeout_sec} sec → killing.")
            p.kill()
            p.join()
            return None, None

        if "error" in return_dict:
            print(f"[ERROR] {algorithm} crashed: {return_dict['error']}")
            return None, None

        return return_dict.get("result"), return_dict.get("metrics")

    def __add_values(self):
        puzzle_generator = RandomPuzzleGenerator(self.__n)
        data = {"n": self.__n, "clues": puzzle_generator.generate()}

        if not self.__csp_done:
            self.__csp_done = self.__add_current(data, self.__csp_time, "CSP")

        if not self.__a_star_done:
            self.__a_star_done = self.__add_current(data, self.__a_star_time, "A*")

        if not self.__hill_done:
            self.__hill_done = self.__add_current(data, self.__hill_time, "HillClimb")

    def __add_current(self, data, lst: list, algorithm: str):
        try:
            result, metrics = self.__run_with_isolation(data, algorithm)

            if metrics is None or "runtime_sec" not in metrics:
                return self.__handle_failure(algorithm)

            self.__fail_counts[algorithm] = 0

            lst.append(metrics["runtime_sec"])

            if len(lst) >= 20:
                prev_mean = mean(lst[:-1])
                curr_mean = mean(lst)
                if abs(prev_mean - curr_mean) < self.__threshold:
                    print(f"[STABLE] {algorithm} mean stabilized at {curr_mean:.4f} sec")
                    return True

            return False

        except Exception as e:
            print(f"[WARNING] {algorithm} crashed with exception: {e}")
            return self.__handle_failure(algorithm)

    def __handle_failure(self, algorithm: str):
        self.__fail_counts[algorithm] += 1

        if self.__fail_counts[algorithm] >= 10:
            print(f"[FAIL] {algorithm} failed 10 times → giving up.")
            return True

        return False

    def evaluate_algorithms(self):
        while not (self.__csp_done and self.__a_star_done and self.__hill_done):
            self.__add_values()

        def safe_stats(lst):
            return (mean(lst) if lst else None,
                    stdev(lst) if len(lst) > 1 else None)

        return (
            *safe_stats(self.__csp_time),
            *safe_stats(self.__a_star_time),
            *safe_stats(self.__hill_time),
        )

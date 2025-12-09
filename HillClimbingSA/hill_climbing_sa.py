import random
import math
import time
from typing import Dict, List, Tuple, Optional
from collections import deque

from SharedFunctions.shared_functions import visible_count


class HillClimbSolver:
    @staticmethod
    def solve(data: dict) -> Tuple[Optional[Dict[Tuple[int, int], int]], Dict[str, object]]:
        solver = HillClimbSolver(data)
        return solver.__run()

    def __init__(self, data: dict):
        self.__start_time = time.time()
        self.__data = data
        self.__n: int = int(data["n"])
        self.__clues = data["clues"]

        self.__max_restarts = 12
        self.__max_iters_per_restart = max(2000, 250 * self.__n)
        self.__patience = 500

        self.__initial_temp = 1.0
        self.__final_temp = 1e-3

        self.__tabu_size = 100
        self.__allow_sideways = True
        self.__sideways_prob_start = 0.5
        self.__perturb_frequency = 300
        self.__perturb_strength = 1

        self.__seed: Optional[int] = None
        if self.__seed is not None:
            random.seed(self.__seed)

        self.__iterations = 0
        self.__restarts = 0
        self.__best_score = float("inf")
        self.__best_grid: Optional[List[List[int]]] = None

    def __run(self) -> Tuple[Optional[Dict[Tuple[int, int], int]], Dict[str, object]]:
        for restart in range(self.__max_restarts):
            self.__restarts += 1

            # initialize grid and tabu
            grid = self.__random_initial_grid()
            tabu = deque(maxlen=self.__tabu_size)   # stores normalized swap keys (r,c1,c2)
            tabu_set = set()

            score = self.__score_grid(grid)
            if score < self.__best_score:
                self.__update_best(grid, score)

            if score == 0:
                return self.__format_result(self.__best_grid, True)

            iters_since_improve = 0
            max_it = self.__max_iters_per_restart

            for it in range(max_it):
                self.__iterations += 1
                frac = it / max(1, max_it - 1)
                temp = max(self.__final_temp, self.__initial_temp * (1 - frac))

                # decaying sideways probability
                sideways_prob = self.__sideways_prob_start * (1.0 - frac) if self.__allow_sideways else 0.0

                # periodically apply a small perturbation to escape deep basins
                if it > 0 and (it % self.__perturb_frequency) == 0:
                    self.__apply_perturbation(grid, strength=self.__perturb_strength)
                    # recompute score fully after perturbation
                    score = self.__score_grid(grid)
                    # clear some tabu to allow new moves
                    tabu.clear()
                    tabu_set.clear()
                    if score < self.__best_score:
                        self.__update_best(grid, score)
                    # reset stagnation counter a bit
                    iters_since_improve = 0
                    continue

                r = random.randrange(self.__n)
                c1, c2 = random.sample(range(self.__n), 2)

                # normalize swap key so c1 < c2 for consistency
                a_c1, a_c2 = (c1, c2) if c1 < c2 else (c2, c1)
                swap_key = (r, a_c1, a_c2)

                # compute delta for the candidate swap
                delta = self.__delta_swap_row(grid, r, c1, c2)

                # tabu: if swap is in tabu_set and move is non-improving, skip it
                if swap_key in tabu_set and delta >= 0:
                    # skip this move; count as one attempt - try next iteration
                    iters_since_improve += 1
                    # possibly trigger small random shuffle to escape if stagnating
                    if iters_since_improve > self.__patience // 2 and random.random() < 0.05:
                        self.__apply_perturbation(grid, strength=1)
                        score = self.__score_grid(grid)
                        if score < self.__best_score:
                            self.__update_best(grid, score)
                        iters_since_improve = 0
                    continue

                # acceptance rule: improvement, or SA probability, or sideways with decaying prob
                accept = False
                if delta < 0:
                    accept = True
                elif delta == 0 and random.random() < sideways_prob:
                    accept = True
                else:
                    # simulated annealing style chance to accept worsening move
                    prob = math.exp(-delta / (temp + 1e-12)) if temp > 0 else 0.0
                    if random.random() < prob:
                        accept = True

                if accept:
                    # perform swap
                    grid[r][c1], grid[r][c2] = grid[r][c2], grid[r][c1]
                    score += delta

                    # push swap into tabu (normalized)
                    tabu.append(swap_key)
                    tabu_set.add(swap_key)
                    # keep tabu_set consistent with deque
                    if len(tabu) == self.__tabu_size:
                        # deque will pop left when full automatically, but we need to remove from set
                        # so rebuild set (small cost) - simpler and robust
                        tabu_set = set(tabu)

                    # update best if improved
                    if score < self.__best_score:
                        self.__update_best(grid, score)
                        iters_since_improve = 0
                    else:
                        # reset on any acceptance that improves or is sideways; if it's worsening, increment
                        iters_since_improve = 0 if delta <= 0 else iters_since_improve + 1
                else:
                    iters_since_improve += 1

                # global success check
                if self.__best_score == 0:
                    return self.__format_result(self.__best_grid, True)

                # if stagnation persists, break and restart (but allow a few restarts)
                if iters_since_improve > self.__patience:
                    break

            # end of one restart loop

        success = self.__best_score == 0
        return self.__format_result(self.__best_grid, success)

    def __random_initial_grid(self) -> List[List[int]]:
        base = list(range(1, self.__n + 1))
        grid: List[List[int]] = []
        for _ in range(self.__n):
            row = base[:]
            random.shuffle(row)
            grid.append(row)
        return grid

    def __apply_perturbation(self, grid: List[List[int]], strength: int = 1) -> None:
        """
        Apply a small random perturbation: pick `strength` rows and shuffle them
        slightly (perform some random swaps inside the row). Keeps rows as permutations.
        """
        n = self.__n
        for _ in range(strength):
            r = random.randrange(n)
            # perform a few random swaps inside the chosen row
            swaps = max(1, n // 4)
            for _ in range(swaps):
                c1, c2 = random.sample(range(n), 2)
                grid[r][c1], grid[r][c2] = grid[r][c2], grid[r][c1]

    def __update_best(self, grid: List[List[int]], score: float) -> None:
        self.__best_score = score
        self.__best_grid = [row[:] for row in grid]

    def __score_grid(self, grid: List[List[int]]) -> float:
        dup_penalty = 0
        for c in range(self.__n):
            seen = set()
            for r in range(self.__n):
                v = grid[r][c]
                if v in seen:
                    dup_penalty += 1
                else:
                    seen.add(v)

        clue_penalty = 0
        for r in range(self.__n):
            row = grid[r]
            left_vis = visible_count(row)
            right_vis = visible_count(reversed(row))
            clue_penalty += abs(left_vis - int(self.__clues["left"][r]))
            clue_penalty += abs(right_vis - int(self.__clues["right"][r]))

        for c in range(self.__n):
            col = [grid[r][c] for r in range(self.__n)]
            top_vis = visible_count(col)
            bottom_vis = visible_count(reversed(col))
            clue_penalty += abs(top_vis - int(self.__clues["top"][c]))
            clue_penalty += abs(bottom_vis - int(self.__clues["bottom"][c]))

        return dup_penalty + 1.5 * clue_penalty

    def __delta_swap_row(self, grid: List[List[int]], r: int, c1: int, c2: int) -> float:
        """
        Compute change in score if we swap grid[r][c1] and grid[r][c2].
        Uses same scoring as __score_grid but computes local differences only.
        """
        n = self.__n
        a = grid[r][c1]
        b = grid[r][c2]

        if a == b:
            return 0.0

        delta = 0.0

        # column duplicate delta for two affected columns
        for c, val_before, val_after in ((c1, a, b), (c2, b, a)):
            before_count = 0
            after_count = 0
            seen_before = set()
            seen_after = set()
            for rr in range(n):
                v = grid[rr][c]
                if rr == r:
                    v_before = val_before
                    v_after = val_after
                else:
                    v_before = v_after = v

                if v_before in seen_before:
                    before_count += 1
                else:
                    seen_before.add(v_before)

                if v_after in seen_after:
                    after_count += 1
                else:
                    seen_after.add(v_after)

            delta += (after_count - before_count)

        # row visibility delta
        row = grid[r][:]
        left_before = visible_count(row)
        right_before = visible_count(reversed(row))

        row[c1], row[c2] = row[c2], row[c1]
        left_after = visible_count(row)
        right_after = visible_count(reversed(row))

        delta += 1.5 * (abs(left_after - int(self.__clues["left"][r])) +
                        abs(right_after - int(self.__clues["right"][r])) -
                        (abs(left_before - int(self.__clues["left"][r])) +
                         abs(right_before - int(self.__clues["right"][r]))))

        # column visibility delta for the two affected columns
        for c, val_before, val_after in ((c1, a, b), (c2, b, a)):
            col_before = [grid[rr][c] if rr != r else val_before for rr in range(n)]
            col_after = [grid[rr][c] if rr != r else val_after for rr in range(n)]

            top_before = visible_count(col_before)
            bottom_before = visible_count(reversed(col_before))
            top_after = visible_count(col_after)
            bottom_after = visible_count(reversed(col_after))

            delta += 1.5 * ((abs(top_after - int(self.__clues["top"][c])) +
                             abs(bottom_after - int(self.__clues["bottom"][c]))) -
                            (abs(top_before - int(self.__clues["top"][c])) +
                             abs(bottom_before - int(self.__clues["bottom"][c]))))

        return delta

    def __format_result(self, grid: Optional[List[List[int]]], success: bool) -> Tuple[Optional[Dict[Tuple[int, int], int]], Dict[str, object]]:
        metrics = {
            "runtime_sec": round(time.time() - self.__start_time, 4),
            "iterations": self.__iterations,
            "restarts": self.__restarts,
            "final_score": None if self.__best_score == float("inf") else self.__best_score,
            "success": bool(success),
            "n": self.__n,
        }

        if not success or grid is None:
            return None, metrics

        solution: Dict[Tuple[int, int], int] = {}
        for r in range(self.__n):
            for c in range(self.__n):
                solution[(r, c)] = int(grid[r][c])

        return solution, metrics
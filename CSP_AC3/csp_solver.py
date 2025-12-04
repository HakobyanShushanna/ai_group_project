import time
import tracemalloc
import itertools
from collections import deque
from SharedFunctions.shared_functions import visible_count
import copy

class CSPSolver:
    def __init__(self, puzzle_data):
        self.__n = puzzle_data["n"]
        self.__clues = puzzle_data["clues"]
        self.__domains = {(r, c): set(range(1, self.__n + 1)) for r in range(self.__n) for c in range(self.__n)}
        self.__assignment = {}

        self.__row_sequences = {r: self.__generate_line_sequences(self.__clues["left"][r],
                                                                  self.__clues["right"][r]) for r in range(self.__n)}
        self.__col_sequences = {c: self.__generate_line_sequences(self.__clues["top"][c],
                                                                  self.__clues["bottom"][c]) for c in range(self.__n)}
        self.__row_possible = {r: list(self.__row_sequences[r]) for r in range(self.__n)}
        self.__col_possible = {c: list(self.__col_sequences[c]) for c in range(self.__n)}

        self.__backtrack_count = 0
        self.__assignment_attempts = 0
        self.__ac3_reductions = 0
        self.__ac3_checks = 0
        self.__ac3_prunes = 0
        self.__nodes_expanded = 0
        self.__runtime = 0
        self.__memory_peak = 0

    def __generate_line_sequences(self, clue_left, clue_right):
        seqs = []
        all_perm = itertools.permutations(range(1, self.__n + 1), self.__n)
        for p in all_perm:
            ok = True
            if clue_left != "":
                if visible_count(list(p)) != int(clue_left):
                    ok = False
            if ok and clue_right != "":
                if visible_count(list(p[::-1])) != int(clue_right):
                    ok = False
            if ok:
                seqs.append(tuple(p))
        return seqs

    def __filter_row_possible(self, r):
        filtered = []
        for seq in self.__row_possible[r]:
            ok = True
            for c in range(self.__n):
                if seq[c] not in self.__domains[(r, c)]:
                    ok = False
                    break
            if ok:
                filtered.append(seq)
        self.__row_possible[r] = filtered
        return filtered

    def __filter_col_possible(self, c):
        filtered = []
        for seq in self.__col_possible[c]:
            ok = True
            for r in range(self.__n):
                if seq[r] not in self.__domains[(r, c)]:
                    ok = False
                    break
            if ok:
                filtered.append(seq)
        self.__col_possible[c] = filtered
        return filtered

    def __get_neighbors(self, cell):
        r, c = cell
        neighbors = [(r, j) for j in range(self.__n) if j != c] + [(i, c) for i in range(self.__n) if i != r]
        return neighbors

    def __revise(self, xi):
        revised = False
        r, c = xi
        to_remove = set()
        self.__filter_row_possible(r)
        self.__filter_col_possible(c)

        for vi in set(self.__domains[xi]):
            self.__ac3_checks += 1
            row_support = any(seq[c] == vi for seq in self.__row_possible[r])
            col_support = any(seq[r] == vi for seq in self.__col_possible[c])
            if not (row_support and col_support):
                to_remove.add(vi)

        if to_remove:
            for v in to_remove:
                if v in self.__domains[xi]:
                    self.__domains[xi].remove(v)
                    self.__ac3_prunes += 1
            revised = True
            self.__ac3_reductions += 1

        return revised

    def __ac3(self):
        queue = deque([(r, c) for r in range(self.__n) for c in range(self.__n)])
        while queue:
            xi = queue.popleft()
            if self.__revise(xi):
                if not self.__domains[xi]:
                    return False
                for xk in self.__get_neighbors(xi):
                    queue.append(xk)
                r, c = xi
                for j in range(self.__n):
                    if (r, j) != xi:
                        queue.append((r, j))
                for i in range(self.__n):
                    if (i, c) != xi:
                        queue.append((i, c))
        return True

    def __consistent(self, var, value):
        r, c = var
        for j in range(self.__n):
            if (r, j) in self.__assignment and self.__assignment[(r, j)] == value:
                return False
        for i in range(self.__n):
            if (i, c) in self.__assignment and self.__assignment[(i, c)] == value:
                return False

        temp_assignment = self.__assignment.copy()
        temp_assignment[var] = value

        row_vals = [temp_assignment.get((r, j)) for j in range(self.__n)]
        if all(v is not None for v in row_vals):
            left = self.__clues["left"][r]
            right = self.__clues["right"][r]
            if left != "" and visible_count(row_vals) != int(left):
                return False
            if right != "" and visible_count(row_vals[::-1]) != int(right):
                return False

        col_vals = [temp_assignment.get((i, c)) for i in range(self.__n)]
        if all(v is not None for v in col_vals):
            top = self.__clues["top"][c]
            bottom = self.__clues["bottom"][c]
            if top != "" and visible_count(col_vals) != int(top):
                return False
            if bottom != "" and visible_count(col_vals[::-1]) != int(bottom):
                return False

        if value not in self.__domains[var]:
            return False

        return True

    def __backtrack(self):
        self.__nodes_expanded += 1
        if len(self.__assignment) == self.__n * self.__n:
            return dict(self.__assignment)

        unassigned = [v for v in self.__domains if v not in self.__assignment]
        var = min(unassigned, key=lambda v: (len(self.__domains[v]), -len(self.__get_neighbors(v))))

        domain_snapshot = copy.deepcopy(self.__domains)
        row_possible_snapshot = copy.deepcopy(self.__row_possible)
        col_possible_snapshot = copy.deepcopy(self.__col_possible)

        for value in sorted(self.__domains[var]):
            self.__assignment_attempts += 1
            if self.__consistent(var, value):
                self.__assignment[var] = value
                self.__domains[var] = {value}

                ac3_ok = self.__ac3()
                if ac3_ok:
                    result = self.__backtrack()
                    if result:
                        return result

                self.__backtrack_count += 1
                self.__domains = copy.deepcopy(domain_snapshot)
                self.__row_possible = copy.deepcopy(row_possible_snapshot)
                self.__col_possible = copy.deepcopy(col_possible_snapshot)
                del self.__assignment[var]

        self.__domains = domain_snapshot
        self.__row_possible = row_possible_snapshot
        self.__col_possible = col_possible_snapshot
        return None

    @staticmethod
    def solve(puzzle_data):
        solver = CSPSolver(puzzle_data)
        tracemalloc.start()
        start_time = time.time()

        solver.__ac3()
        result = solver.__backtrack()

        solver.__runtime = time.time() - start_time
        _, peak = tracemalloc.get_traced_memory()
        solver.__memory_peak = peak
        tracemalloc.stop()

        metrics = {
            "runtime_sec": round(solver.__runtime, 4),
            "backtracks": solver.__backtrack_count,
            "assignments_attempted": solver.__assignment_attempts,
            "nodes_expanded": solver.__nodes_expanded,
            "ac3_checks": solver.__ac3_checks,
            "ac3_prunes": solver.__ac3_prunes,
            "ac3_reductions": solver.__ac3_reductions,
            "memory_peak_bytes": solver.__memory_peak
        }

        return result, metrics
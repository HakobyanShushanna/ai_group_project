import heapq
import time
from SharedFunctions.shared_functions import visible_count

class AStarSolver:
    def __init__(self, data, weight=1.0):
        self.__n = data["n"]
        self.__clues = data["clues"]
        self.__initial_grid = data["grid"]
        self.__weight = weight

        self.__expanded = 0
        self.__generated = 0
        self.__start_time = time.time()

    def solve(self):
        start = self.__parse_initial_grid()

        pq = []
        g0 = 0
        h0 = self.__heuristic(start)
        f0 = g0 + self.__weight * h0

        heapq.heappush(pq, (f0, g0, start))
        visited = set()

        while pq:
            f, g, grid = heapq.heappop(pq)
            self.__expanded += 1

            state_key = AStarSolver.__freeze(grid)
            if state_key in visited:
                continue
            visited.add(state_key)

            if self.__is_goal(grid):
                return self.__grid_to_solution(grid), self.__metrics()

            for nxt in self.__next_states(grid):
                g2 = g + 1
                h2 = self.__heuristic(nxt)
                f2 = g2 + self.__weight * h2
                heapq.heappush(pq, (f2, g2, nxt))

        return None, {"error": "No solution found"}

    def __parse_initial_grid(self):
        return [
            [int(x) if str(x).isdigit() else 0 for x in row]
            for row in self.__initial_grid
        ]

    @staticmethod
    def __freeze(grid):
        return tuple(tuple(r) for r in grid)

    def __is_goal(self, grid):
        n = self.__n

        for r in range(n):
            row = grid[r]
            if 0 in row or len(set(row)) != n:
                return False

        for c in range(n):
            col = [grid[r][c] for r in range(n)]
            if len(set(col)) != n:
                return False

        return self.__check_clues(grid)

    def __check_clues(self, grid):
        n = self.__n
        clues = self.__clues

        for c, clue in enumerate(clues["top"]):
            if clue != 0:
                if visible_count([grid[r][c] for r in range(n)]) != clue:
                    return False

        for c, clue in enumerate(clues["bottom"]):
            if clue != 0:
                if visible_count([grid[r][c] for r in reversed(range(n))]) != clue:
                    return False

        for r, clue in enumerate(clues["left"]):
            if clue != 0:
                if visible_count(grid[r]) != clue:
                    return False

        for r, clue in enumerate(clues["right"]):
            if clue != 0:
                if visible_count(list(reversed(grid[r]))) != clue:
                    return False

        return True

    def __heuristic(self, grid):
        h = 0
        n = self.__n

        for r in range(n):
            row = [x for x in grid[r] if x != 0]
            if len(row) != len(set(row)):
                h += 1

        for c in range(n):
            col = [grid[r][c] for r in range(n) if grid[r][c] != 0]
            if len(col) != len(set(col)):
                h += 1

        for c, clue in enumerate(self.__clues["top"]):
            if clue != 0:
                col = [grid[r][c] for r in range(n) if grid[r][c] != 0]
                if col and visible_count(col) > clue:
                    h += 1

        return h

    def __next_states(self, grid):
        n = self.__n

        for r in range(n):
            row = grid[r]
            for c in range(n):
                if row[c] == 0:
                    row_used = set(row)
                    col_used = {grid[x][c] for x in range(n)}
                    allowed = {v for v in range(1, n + 1)
                               if v not in row_used and v not in col_used}

                    for v in allowed:
                        new_grid = [r2[:] for r2 in grid]
                        new_grid[r][c] = v
                        self.__generated += 1
                        yield new_grid

                    return

    def __grid_to_solution(self, grid):
        sol = {}
        for r in range(self.__n):
            for c in range(self.__n):
                sol[(r, c)] = grid[r][c]
        return sol

    def __metrics(self):
        return {
            "expanded_nodes": self.__expanded,
            "generated_nodes": self.__generated,
            "runtime_seconds": round(time.time() - self.__start_time, 4),
            "algorithm": f"A* (w={self.__weight})",
        }
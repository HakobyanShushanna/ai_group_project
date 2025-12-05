import heapq
import time
from functools import lru_cache
from SharedFunctions.shared_functions import visible_count

class AStarSolver:
    def __init__(self, data, weight=2.0):
        self.__n = data["n"]
        self.__clues = data["clues"]
        self.__initial_grid = [
            [int(x) if str(x).isdigit() else 0 for x in row]
            for row in data["grid"]
        ]
        self.__weight = float(weight)

        self.__full_mask = (1 << self.__n) - 1
        self.__val_to_mask = {v: 1 << (v - 1) for v in range(1, self.__n + 1)}

        self.__expanded = 0
        self.__generated = 0
        self.__start_time = time.time()

    @staticmethod
    @lru_cache(maxsize=None)
    def __visible_cached_tuple(seq_tuple):
        seq = [x for x in seq_tuple if x != 0]
        return visible_count(seq)

    @lru_cache(maxsize=200000)
    def __heuristic_cached(self, state_key):
        flat_bytes, row_masks, col_masks = state_key
        n = self.__n
        clues = self.__clues
        h = 0

        flat = list(flat_bytes)

        for r in range(n):
            row_off = r * n
            row_vals = tuple(flat[row_off + c] for c in range(n))
            nonzero = tuple(v for v in row_vals if v != 0)
            if nonzero and len(nonzero) != len(set(nonzero)):
                h += 4
            clue = clues["left"][r]
            if clue != 0 and nonzero:
                v = AStarSolver.__visible_cached_tuple(nonzero)
                empties = n - len(nonzero)
                if v > clue:
                    h += 5
                if v + empties < clue:
                    h += 5
            clue = clues["right"][r]
            if clue != 0 and nonzero:
                rev = tuple(reversed(nonzero))
                v = AStarSolver.__visible_cached_tuple(rev)
                empties = n - len(nonzero)
                if v > clue:
                    h += 5
                if v + empties < clue:
                    h += 5

        for c in range(n):
            col_vals = tuple(flat[c + r * n] for r in range(n))
            nonzero = tuple(v for v in col_vals if v != 0)
            if nonzero and len(nonzero) != len(set(nonzero)):
                h += 4
            clue = clues["top"][c]
            if clue != 0 and nonzero:
                v = AStarSolver.__visible_cached_tuple(nonzero)
                empties = n - len(nonzero)
                if v > clue:
                    h += 5
                if v + empties < clue:
                    h += 5
            clue = clues["bottom"][c]
            if clue != 0 and nonzero:
                rev = tuple(reversed(nonzero))
                v = AStarSolver.__visible_cached_tuple(rev)
                empties = n - len(nonzero)
                if v > clue:
                    h += 5
                if v + empties < clue:
                    h += 5

        total_empty = flat.count(0)
        if total_empty:
            h += total_empty // max(1, self.__n // 2)

        return h

    def solve(self):
        start_flat = [0] * (self.__n * self.__n)
        row_masks = [0] * self.__n
        col_masks = [0] * self.__n

        for r in range(self.__n):
            for c in range(self.__n):
                v = self.__initial_grid[r][c]
                if v:
                    start_flat[r * self.__n + c] = v
                    mask = self.__val_to_mask[v]
                    row_masks[r] |= mask
                    col_masks[c] |= mask

        for r in range(self.__n):
            assigned_count = sum(1 for c in range(self.__n) if start_flat[r * self.__n + c] != 0)
            if row_masks[r].bit_count() != assigned_count:
                return None, {"error": "Invalid initial grid: duplicate in row"}
        for c in range(self.__n):
            assigned_count = sum(1 for r in range(self.__n) if start_flat[r * self.__n + c] != 0)
            if col_masks[c].bit_count() != assigned_count:
                return None, {"error": "Invalid initial grid: duplicate in col"}

        start_bytes = bytes(start_flat)
        row_masks_t = tuple(row_masks)
        col_masks_t = tuple(col_masks)

        pq = []
        counter = 0
        g0 = 0
        start_state_key = (start_bytes, row_masks_t, col_masks_t)
        h0 = self.__heuristic_cached(start_state_key)
        f0 = g0 + self.__weight * h0

        heapq.heappush(pq, (f0, counter, g0, start_bytes, row_masks_t, col_masks_t))
        counter += 1

        visited = {start_state_key: 0}

        while pq:
            f, _, g, flat_bytes, row_masks_t, col_masks_t = heapq.heappop(pq)
            self.__expanded += 1

            if self.__is_goal_state(flat_bytes, row_masks_t, col_masks_t):
                grid = self.__bytes_to_grid(flat_bytes)
                return self.__grid_to_solution(grid), self.__metrics()

            n = self.__n
            flat = list(flat_bytes)
            full_mask = self.__full_mask
            best_r = best_c = -1
            best_mask = None
            best_count = None

            for r in range(n):
                rm = row_masks_t[r]
                base = r * n
                for c in range(n):
                    if flat[base + c] == 0:
                        cm = col_masks_t[c]
                        allowed = full_mask & ~(rm | cm)
                        if allowed == 0:
                            best_count = 0
                            break
                        cnt = allowed.bit_count()
                        if best_count is None or cnt < best_count:
                            best_count = cnt
                            best_mask = allowed
                            best_r, best_c = r, c
                            if cnt == 1:
                                break
                if best_count == 0 or best_count == 1:
                    break

            if best_count is None:
                continue
            if best_count == 0:
                continue

            m = best_mask
            candidates = []
            while m:
                lb = m & -m
                bit_index = (lb.bit_length() - 1)
                val = bit_index + 1

                child_flat = bytearray(flat_bytes)
                idx = best_r * n + best_c
                child_flat[idx] = val
                child_bytes = bytes(child_flat)

                new_row_masks = list(row_masks_t)
                new_col_masks = list(col_masks_t)
                maskv = self.__val_to_mask[val]
                new_row_masks[best_r] |= maskv
                new_col_masks[best_c] |= maskv
                new_row_masks_t = tuple(new_row_masks)
                new_col_masks_t = tuple(new_col_masks)

                child_state_key = (child_bytes, new_row_masks_t, new_col_masks_t)
                h_child = self.__heuristic_cached(child_state_key)
                candidates.append((h_child, val, child_bytes, new_row_masks_t, new_col_masks_t))

                m -= lb

            candidates.sort(key=lambda x: x[0])

            for _, val, child_bytes, child_row_masks_t, child_col_masks_t in candidates:
                g2 = g + 1
                child_key = (child_bytes, child_row_masks_t, child_col_masks_t)
                prev_g = visited.get(child_key)
                if prev_g is not None and prev_g <= g2:
                    continue
                visited[child_key] = g2

                h2 = self.__heuristic_cached(child_key)
                f2 = g2 + self.__weight * h2

                heapq.heappush(pq, (f2, counter, g2, child_bytes, child_row_masks_t, child_col_masks_t))
                counter += 1
                self.__generated += 1

        return None, {"error": "No solution found", **self.__metrics()}

    def __bytes_to_grid(self, b):
        n = self.__n
        flat = list(b)
        return [flat[i * n:(i + 1) * n] for i in range(n)]

    def __is_goal_state(self, flat_bytes, row_masks_t, col_masks_t):
        n = self.__n
        flat = list(flat_bytes)

        if 0 in flat:
            return False

        for r in range(n):
            if row_masks_t[r].bit_count() != n:
                return False
        for c in range(n):
            if col_masks_t[c].bit_count() != n:
                return False

        return self.__check_clues_bytes(flat_bytes)

    def __check_clues_bytes(self, flat_bytes):
        n = self.__n
        clues = self.__clues
        flat = list(flat_bytes)
        vis = AStarSolver.__visible_cached_tuple

        for c, clue in enumerate(clues["top"]):
            if clue != 0:
                col = tuple(flat[r * n + c] for r in range(n))
                if vis(col) != clue:
                    return False

        for c, clue in enumerate(clues["bottom"]):
            if clue != 0:
                col = tuple(flat[r * n + c] for r in reversed(range(n)))
                if vis(col) != clue:
                    return False

        for r, clue in enumerate(clues["left"]):
            if clue != 0:
                row = tuple(flat[r * n + c] for c in range(n))
                if vis(row) != clue:
                    return False

        for r, clue in enumerate(clues["right"]):
            if clue != 0:
                row = tuple(flat[r * n + c] for c in reversed(range(n)))
                if vis(row) != clue:
                    return False
        return True

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
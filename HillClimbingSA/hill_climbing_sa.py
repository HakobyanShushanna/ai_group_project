import random
import math

class HillClimbSolver:
    @staticmethod
    def solve(data, max_iters=10000, temp=100.0, cooling_rate=0.995):
        n = data["n"]
        clues = data["clues"]

        current = [
            [int(cell) if isinstance(cell, int) or cell.isdigit() else random.randint(1, n)
             for cell in row] for row in data["grid"]
        ]
        best = [row[:] for row in current]
        best_score = HillClimbSolver.__evaluate(best, clues)

        metrics = {"iterations": 0, "best_score": best_score, "temperature": temp}

        for iteration in range(max_iters):
            metrics["iterations"] += 1
            neighbor = HillClimbSolver.__neighbor(current, n)
            neighbor_score = HillClimbSolver.__evaluate(neighbor, clues)

            delta = neighbor_score - HillClimbSolver.__evaluate(current, clues)
            if delta > 0 or random.random() < math.exp(delta / temp):
                current = [row[:] for row in neighbor]
                if neighbor_score > best_score:
                    best = [row[:] for row in neighbor]
                    best_score = neighbor_score

            temp *= cooling_rate
            metrics["temperature"] = temp

            if best_score == n * n:
                break

        solution = {(r, c): best[r][c] for r in range(n) for c in range(n)}
        metrics["best_score"] = best_score
        return solution, metrics

    @staticmethod
    def __neighbor(grid, n):
        new_grid = [row[:] for row in grid]
        r = random.randint(0, n - 1)
        c = random.randint(0, n - 1)
        new_grid[r][c] = random.randint(1, n)
        return new_grid

    @staticmethod
    def __evaluate(grid, clues):
        def visible_count(line):
            max_height, count = 0, 0
            for h in line:
                if h > max_height:
                    max_height = h
                    count += 1
            return count

        n = len(grid)
        score = 0
        for i in range(n):
            row = grid[i]
            col = [grid[r][i] for r in range(n)]

            if clues["top"][i] and visible_count(col) == clues["top"][i]:
                score += 1
            if clues["bottom"][i] and visible_count(col[::-1]) == clues["bottom"][i]:
                score += 1
            if clues["left"][i] and visible_count(row) == clues["left"][i]:
                score += 1
            if clues["right"][i] and visible_count(row[::-1]) == clues["right"][i]:
                score += 1
        return score
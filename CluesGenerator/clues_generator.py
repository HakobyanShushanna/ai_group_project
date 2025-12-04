import random
from SharedFunctions.shared_functions import visible_count

class RandomPuzzleGenerator:
    def __init__(self, n: int):
        self.n = n

    def __generate_latin_square(self):
        n = self.n
        return [[(i + j) % n + 1 for j in range(n)] for i in range(n)]

    def __randomize_latin_square(self, grid):
        n = self.n

        rows = list(range(n))
        random.shuffle(rows)
        grid = [grid[r] for r in rows]

        cols = list(range(n))
        random.shuffle(cols)
        grid = [[row[c] for c in cols] for row in grid]

        symbols = list(range(1, n + 1))
        random.shuffle(symbols)
        mapping = {old: new for old, new in zip(range(1, n + 1), symbols)}

        grid = [[mapping[value] for value in row] for row in grid]

        return grid

    def __compute_clues(self, grid):
        n = self.n

        top = []
        bottom = []
        left = []
        right = []

        for c in range(n):
            col = [grid[r][c] for r in range(n)]
            top.append(visible_count(col))
            bottom.append(visible_count(col[::-1]))

        for r in range(n):
            row = grid[r]
            left.append(visible_count(row))
            right.append(visible_count(row[::-1]))

        return {
            "top": top,
            "bottom": bottom,
            "left": left,
            "right": right
        }

    def generate(self):
        latin = self.__generate_latin_square()
        grid = self.__randomize_latin_square(latin)
        clues = self.__compute_clues(grid)
        return clues
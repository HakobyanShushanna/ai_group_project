class DataChecker:
    def __init__(self, data: dict):
        self.__n = data["n"]
        self.__clues = data["clues"]

        if not self.__convert_int():
            raise ValueError("DataChecker initialization failed: clues contain invalid data types.")

    def __convert_int(self) -> bool:
        for direction in self.__clues:
            for i in range(len(self.__clues[direction])):
                try:
                    self.__clues[direction][i] = int(self.__clues[direction][i])
                except Exception:
                    print(f"Incorrect data type in {direction} at index {i}: {self.__clues[direction][i]!r}")
                    return False
        return True

    def general_check(self)->bool:
        return self.__check_length() and self.__check_values() and self.__check_opposite_sums()

    def __check_length(self)->bool:
        return ((len(self.__clues["top"]) + len(self.__clues["bottom"])
                 + len(self.__clues["left"]) + len(self.__clues["right"])) == (4 * self.__n))

    def __check_values(self)->bool:
        for direction in self.__clues:
            for clue in self.__clues[direction]:
                if clue < 1 or clue > self.__n:
                    return False
        return True

    def __check_opposite_sums(self)->bool:
        dir1 = "top"
        dir2 = "bottom"

        for i in range(0, self.__n):
            if ((3 > self.__clues[dir1][i] + self.__clues[dir2][i]) or
                    (self.__clues[dir1][i] + self.__clues[dir2][i] > self.__n + 1)):
                return False

        dir1 = "left"
        dir2 = "right"

        for i in range(0, self.__n):
            if ((3 > self.__clues[dir1][i] + self.__clues[dir2][i]) or
                    (self.__clues[dir1][i] + self.__clues[dir2][i] > self.__n + 1)):
                return False

        return True
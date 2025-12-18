class Position:
    def __init__(self, row: int, col: int):
        if not (0 <= row < 8) or not (0 <= col < 8):
            raise ValueError("行と列は0から7の範囲内である必要があります。")

        self._row = row
        self._col = col

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    @property
    def row(self) -> int:
        return self._row

    @property
    def col(self) -> int:
        return self._col
class Position:
    def __init__(self, row: int, col: int):
        if not (0 <= row < 8) or not (0 <= col < 8):
            raise ValueError("行と列は0から7の範囲内である必要があります。")

        self._row = row
        self._col = col

    @property
    def row(self) -> int:
        return self._row

    @property
    def col(self) -> int:
        return self._col

from .disc import Disc
from .position import Position

class Board:
    def __init__(self, cells: dict[Position, Disc]):
        self._cells = cells

    @classmethod
    def create() -> 'Board':
        cells = {}
        for row in range(8):
            for col in range(8):
                pos = Position(row, col)
                cells[pos] = Disc.EMPTY

        cells[Position(3, 3)] = Disc.WHITE
        cells[Position(3, 4)] = Disc.BLACK
        cells[Position(4, 3)] = Disc.BLACK
        cells[Position(4, 4)] = Disc.WHITE

        return Board(cells)

    @classmethod
    def reconstruct(cls, cells: dict[Position, Disc]) -> 'Board':
        return cls(cells)

    @property
    def cells(self) -> dict[Position, Disc]:
        return self._cells

    def get_valid_moves(self, player: Disc.BLACK | Disc.WHITE) -> list[Position]:
        """指定されたプレイヤーが置ける位置を返す"""
        valid_positions = []

        for row in range(8):
            for col in range(8):
                pos = Position(row, col)
                if self._can_place(pos, player):
                    valid_positions.append(pos)

        return valid_positions

    def _can_place(self, position: Position, player: Disc.BLACK | Disc.WHITE) -> bool:
        """指定された位置に石を置けるかチェック"""
        # マスが空でなければ置けない
        if self._cells[position] != Disc.EMPTY:
            return False

        # 8方向をチェックして、1つでも裏返せる石があればTrue
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                      (0, 1), (1, -1), (1, 0), (1, 1)]

        for dr, dc in directions:
            if self._can_flip_in_direction(position, player, dr, dc):
                return True

        return False

    def _can_flip_in_direction(self, position: Position, player: Disc, dr: int, dc: int) -> bool:
        """指定された方向に裏返せる石があるかチェック"""
        opponent = Disc.WHITE if player == Disc.BLACK else Disc.BLACK

        row = position.row + dr
        col = position.col + dc

        # 最初のマスが盤面内かチェック
        if not self._is_valid_position(row, col):
            return False

        # 最初のマスが相手の石かチェック
        first_pos = Position(row, col)
        if self._cells[first_pos] != opponent:
            return False

        # 相手の石が続く間、進む
        row += dr
        col += dc

        while self._is_valid_position(row, col):
            pos = Position(row, col)
            disc = self._cells[pos]

            # 自分の石が見つかったら裏返せる
            if disc == player:
                return True

            # 空のマスが見つかったら裏返せない
            if disc == Disc.EMPTY:
                return False

            # disc == opponent なので続ける
            row += dr
            col += dc

        # 盤面外に出たら裏返せない
        return False

    def _is_valid_position(self, row: int, col: int) -> bool:
        """位置が盤面内かチェック"""
        return 0 <= row < 8 and 0 <= col < 8
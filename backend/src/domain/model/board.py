from .disc import Disc
from .position import Position

class Board:
    def __init__(self, cells: dict[Position, Disc]):
        self._cells = cells

    @classmethod
    def create(cls) -> 'Board':
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

    def place_disc(self, position: Position, disc: Disc) -> None:
        """指定された位置に石を置き、裏返す"""
        if disc == Disc.EMPTY:
            raise ValueError("EMPTYの石は配置できません")
        if not self._can_place(position, disc):
            raise ValueError("指定された位置に石を置くことはできません")

        self._cells[position] = disc

        # 8方向に対して裏返し処理を行う
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                      (0, 1), (1, -1), (1, 0), (1, 1)]

        for dr, dc in directions:
            positions = self._get_flippable_positions_in_direction(position, disc, dr, dc)
            for pos in positions:
                self._cells[pos] = disc

    def get_valid_moves(self, disc: Disc) -> list[Position]:
        """指定されたプレイヤーが置ける位置を返す"""
        if disc == Disc.EMPTY:
            raise ValueError("EMPTYに対する有効な手は取得できません")
        valid_positions = []

        for row in range(8):
            for col in range(8):
                pos = Position(row, col)
                if self._can_place(pos, disc):
                    valid_positions.append(pos)

        return valid_positions

    def _can_place(self, position: Position, disc: Disc) -> bool:
        """指定された位置に石を置けるかチェック"""
        # マスが空でなければ置けない
        if self._cells[position] != Disc.EMPTY:
            return False

        # 8方向をチェックして、1つでも裏返せる石があればTrue
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                      (0, 1), (1, -1), (1, 0), (1, 1)]

        for dr, dc in directions:
            if len(self._get_flippable_positions_in_direction(position, disc, dr, dc)) > 0:
                return True

        return False

    def _get_flippable_positions_in_direction(self, position: Position, disc: Disc, dr: int, dc: int) -> list[Position]:
        """指定された方向で裏返せる石の位置を返す"""
        opponent = Disc.WHITE if disc == Disc.BLACK else Disc.BLACK
        positions_to_flip = []

        row = position.row + dr
        col = position.col + dc

        # 最初のマスが盤面内かチェック
        if not self._is_valid_position(row, col):
            return []

        # 最初のマスが相手の石かチェック
        first_pos = Position(row, col)
        if self._cells[first_pos] != opponent:
            return []

        positions_to_flip.append(first_pos)

        # 相手の石が続く間、進む
        row += dr
        col += dc

        while self._is_valid_position(row, col):
            pos = Position(row, col)
            _disc = self._cells[pos]

            # 自分の石が見つかったら裏返せる位置のリストを返す
            if _disc == disc:
                return positions_to_flip

            # 空のマスが見つかったら裏返せない
            if _disc == Disc.EMPTY:
                return []

            # 相手の石なので追加して続ける
            positions_to_flip.append(pos)
            row += dr
            col += dc

        # 盤面外に出たら裏返せない
        return []

    def _is_valid_position(self, row: int, col: int) -> bool:
        """位置が盤面内かチェック"""
        return 0 <= row < 8 and 0 <= col < 8
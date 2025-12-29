"""位置（Position）に関する例外"""

from .base import DomainException


class PositionException(DomainException):
    pass


class InvalidPositionException(PositionException):
    """盤面外の座標を指定した場合

    リバーシの盤面は8x8 (0-7の範囲)
    """

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        super().__init__(f"位置({row}, {col})は盤面外です。有効範囲は0-7です。")

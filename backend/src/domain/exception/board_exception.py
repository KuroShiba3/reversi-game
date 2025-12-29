from .base import DomainException


class BoardException(DomainException):
    pass


class InvalidMoveException(BoardException):
    """無効な手を打とうとした場合

    - 既に石がある位置には置けない
    - 相手の石を挟めない位置には置けない
    """

    def __init__(
        self,
        row: int,
        col: int,
        disc_name: str,
        reason: str = "指定された位置に石を置くことはできません",
    ):
        self.row = row
        self.col = col
        self.disc_name = disc_name
        self.reason = reason
        super().__init__(f"{disc_name}の石を({row}, {col})に置けません: {reason}")


class CannotPlaceEmptyDiscException(BoardException):
    """EMPTYの石を置こうとした場合

    EMPTYは石ではなく「空きマス」を表す
    """

    def __init__(self):
        super().__init__("EMPTYの石は配置できません")

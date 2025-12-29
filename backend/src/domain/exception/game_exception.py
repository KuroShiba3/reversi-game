from uuid import UUID

from .base import DomainException


class GameException(DomainException):
    pass


class GameAlreadyFinishedException(GameException):
    """既に終了したゲームに対して操作しようとした場合

    終了したゲームは変更不可
    """

    def __init__(self, game_id: UUID):
        self.game_id = game_id
        super().__init__(f"ゲームは既に終了しています: {game_id}")


class CannotPassWithValidMovesException(GameException):
    """有効な手があるのにパスしようとした場合

    置ける場所があればパスできない
    """

    def __init__(self, current_player_name: str, valid_moves_count: int):
        self.current_player_name = current_player_name
        self.valid_moves_count = valid_moves_count
        super().__init__(
            f"{current_player_name}は{valid_moves_count}個の有効な手があるため、パスできません"
        )

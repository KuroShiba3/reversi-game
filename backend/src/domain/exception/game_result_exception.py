from .base import DomainException


class GameResultException(DomainException):
    pass


class InvalidScoreException(GameResultException):
    """不正なスコアが指定された場合

    - スコアは0以上64以下
    - 黒+白の合計は最大64
    """

    def __init__(self, black_score: int, white_score: int, reason: str):
        self.black_score = black_score
        self.white_score = white_score
        self.reason = reason
        super().__init__(f"不正なスコア: 黒={black_score}, 白={white_score} - {reason}")

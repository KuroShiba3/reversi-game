from datetime import datetime
from uuid import UUID

from .disc import Disc


class GameResult:
    def __init__(
        self,
        game_id: UUID,
        winner: Disc.BLACK | Disc.WHITE | None,  # None = DRAW
        black_score: int,
        white_score: int,
        finished_at: datetime,
    ):
        if black_score < 0 or black_score > 64:
            raise ValueError("黒のスコアは0から64の範囲内である必要があります。")
        if white_score < 0 or white_score > 64:
            raise ValueError("白のスコアは0から64の範囲内である必要があります。")

        self._game_id = game_id
        self._winner = winner
        self._black_score = black_score
        self._white_score = white_score
        self._finished_at = finished_at

    @classmethod
    def create(
        cls, game_id: UUID, black_score: int, white_score: int
    ) -> "GameResult":
        """スコアから勝者を判定してGameResultを作成"""
        if black_score > white_score:
            winner = Disc.BLACK
        elif white_score > black_score:
            winner = Disc.WHITE
        else:
            winner = None  # 引き分け

        return cls(game_id, winner, black_score, white_score, datetime.now())

    @classmethod
    def reconstruct(
        cls,
        game_id: UUID,
        winner: Disc.BLACK | Disc.WHITE | None,
        black_score: int,
        white_score: int,
        finished_at: datetime,
    ) -> "GameResult":
        """永続化されたデータからGameResultを再構築"""
        return cls(game_id, winner, black_score, white_score, finished_at)

    @property
    def game_id(self) -> UUID:
        return self._game_id

    @property
    def winner(self) -> Disc.BLACK | Disc.WHITE | None:
        return self._winner

    @property
    def black_score(self) -> int:
        return self._black_score

    @property
    def white_score(self) -> int:
        return self._white_score

    @property
    def finished_at(self) -> datetime:
        return self._finished_at

    def to_db_winner_value(self) -> int:
        """DB保存用のwinner値を返す (1: BLACK, 2: WHITE, 3: DRAW)"""
        if self._winner == Disc.BLACK:
            return 1
        elif self._winner == Disc.WHITE:
            return 2
        else:
            return 3  # DRAW

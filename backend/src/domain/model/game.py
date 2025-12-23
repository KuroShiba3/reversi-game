from uuid import UUID, uuid4

from .board import Board
from .disc import Disc
from .game_result import GameResult
from .game_status import GameStatus
from .position import Position

class Game:
    def __init__(self, id: UUID, board: Board, current_player: Disc, status: GameStatus, result: GameResult | None = None):
        self._id = id
        self._board = board
        self._current_player = current_player
        self._status = status
        self._result = result

    @classmethod
    def create(cls) -> 'Game':
        board = Board.create()
        return cls(uuid4(), board, Disc.BLACK, GameStatus.PLAYING)

    @classmethod
    def reconstruct(cls, id: UUID, board: Board, current_player: Disc, status: GameStatus) -> 'Game':
        return cls(id, board, current_player, status)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def board(self) -> Board:
        return self._board

    @property
    def current_player(self) -> Disc:
        return self._current_player

    @property
    def status(self) -> GameStatus:
        return self._status

    @property
    def result(self) -> GameResult | None:
        return self._result

    def place_disc(self, position: Position, disc: Disc) -> None:
        self.board.place_disc(position, disc)
        # ターンを次のプレイヤーに切り替え
        self._current_player = Disc.WHITE if disc == Disc.BLACK else Disc.BLACK

    def get_valid_moves(self, disc: Disc | None = None) -> list[Position]:
        """
        指定されたプレイヤーの有効な手を取得
        discが指定されない場合は現在のプレイヤーの有効な手を返す
        """
        if self._status == GameStatus.FINISHED:
            return []

        player = disc if disc is not None else self.current_player
        return self.board.get_valid_moves(player)

    def pass_turn(self) -> None:
        # ターンを次のプレイヤーに切り替え
        self._current_player = Disc.WHITE if self.current_player == Disc.BLACK else Disc.BLACK

    def can_current_player_move(self) -> bool:
        """現在のプレイヤーが手を打てるかチェック"""
        return len(self.get_valid_moves()) > 0

    def get_scores(self) -> tuple[int, int]:
        black_score = sum(1 for disc in self.board.cells.values() if disc == Disc.BLACK)
        white_score = sum(1 for disc in self.board.cells.values() if disc == Disc.WHITE)
        return black_score, white_score

    def is_game_over(self) -> bool:
        """ゲームが終了しているかチェック"""
        if self._status == GameStatus.FINISHED:
            return True

        black_moves = self.get_valid_moves(Disc.BLACK)
        white_moves = self.get_valid_moves(Disc.WHITE)

        return len(black_moves) == 0 and len(white_moves) == 0

    def finish(self) -> None:
        """ゲームを終了してGameResultを内部に保持する"""
        if self._status == GameStatus.FINISHED:
            raise ValueError("ゲームはすでに終了しています。")

        black_score, white_score = self.get_scores()
        self._status = GameStatus.FINISHED
        self._result = GameResult.create(self._id, black_score, white_score)
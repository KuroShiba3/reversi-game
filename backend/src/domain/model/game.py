from uuid import UUID, uuid4

from .board import Board
from .disc import Disc
from .position import Position

class Game:
    def __init__(self, id: UUID, board: Board, current_player: Disc.BLACK | Disc.WHITE):
        self._id = id
        self._board = board
        self._current_player = current_player

    @classmethod
    def create(cls) -> 'Game':
        board = Board.create()
        return cls(uuid4(), board, Disc.BLACK)

    @classmethod
    def reconstruct(cls, id: UUID, board: Board, current_player: Disc.BLACK | Disc.WHITE) -> 'Game':
        return cls(id, board, current_player)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def board(self) -> Board:
        return self._board

    @property
    def current_player(self) -> Disc.BLACK | Disc.WHITE:
        return self._current_player

    def place_disc(self, position: Position, disc: Disc.BLACK | Disc.WHITE) -> None:
        self.board.place_disc(position, disc)
        # ターンを次のプレイヤーに切り替え
        self._current_player = Disc.WHITE if disc == Disc.BLACK else Disc.BLACK

    def get_valid_moves(self) -> list[Position]:
        return self.board.get_valid_moves(self.current_player)

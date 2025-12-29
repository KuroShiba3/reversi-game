from pydantic import BaseModel


class Position(BaseModel):
    row: int
    col: int


class CellState(BaseModel):
    row: int
    col: int
    disc: str


class GameStateResponse(BaseModel):
    board_state: list[CellState]
    current_player: str
    black_score: int
    white_score: int
    status: str
    valid_moves: list[Position]


class StartGameResponse(GameStateResponse):
    game_id: str


class PlaceDiscRequest(BaseModel):
    row: int
    col: int

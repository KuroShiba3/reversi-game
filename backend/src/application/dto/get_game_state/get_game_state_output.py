from dataclasses import dataclass

@dataclass(frozen=True)
class GetGameStateOutput:
    board_state: list[dict[str, int | str]]
    current_player: str
    black_score: int
    white_score: int
    status: str
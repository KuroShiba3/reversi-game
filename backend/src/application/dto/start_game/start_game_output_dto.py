from dataclasses import dataclass

@dataclass(frozen=True)
class StartGameOutputDTO:
    game_id: str
    board_state: list[dict[str, int | str]]
    current_player: str
    status: str
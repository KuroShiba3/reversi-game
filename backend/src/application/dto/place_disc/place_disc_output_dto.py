from dataclasses import dataclass

@dataclass(frozen=True)
class PlaceDiscOutputDTO:
    board_state: list[dict[str, int | str]]
    next_player: str

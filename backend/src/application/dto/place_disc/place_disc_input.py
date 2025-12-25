from dataclasses import dataclass

@dataclass(frozen=True)
class PlaceDiscInput:
    game_id: str
    disc: str
    position: dict[str, int]

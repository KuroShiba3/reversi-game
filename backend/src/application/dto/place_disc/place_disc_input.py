from dataclasses import dataclass

@dataclass(frozen=True)
class PlaceDiscInput:
    game_id: str
    position: dict[str, int]

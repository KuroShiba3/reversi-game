from dataclasses import dataclass

@dataclass(frozen=True)
class PlaceDiscInputDTO:
    game_id: str
    disc: str
    position: dict[str, int]

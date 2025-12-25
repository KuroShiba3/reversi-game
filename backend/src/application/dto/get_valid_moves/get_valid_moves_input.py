from dataclasses import dataclass

@dataclass(frozen=True)
class GetValidMovesInput:
    game_id: str
from dataclasses import dataclass

@dataclass(frozen=True)
class GetGameStateInputDTO:
    game_id: str
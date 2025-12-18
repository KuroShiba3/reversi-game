from dataclasses import dataclass

@dataclass(frozen=True)
class PassTurnInputDTO:
    game_id: str


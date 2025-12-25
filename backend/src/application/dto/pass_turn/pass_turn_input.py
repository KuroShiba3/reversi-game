from dataclasses import dataclass

@dataclass(frozen=True)
class PassTurnInput:
    game_id: str


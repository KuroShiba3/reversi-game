from dataclasses import dataclass

@dataclass(frozen=True)
class GetGameStateInput:
    game_id: str
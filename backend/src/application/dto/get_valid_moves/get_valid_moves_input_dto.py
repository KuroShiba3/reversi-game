from dataclasses import dataclass

@dataclass(frozen=True)
class GetValidMovesInputDTO:
    game_id: str
from dataclasses import dataclass

@dataclass(frozen=True)
class GetValidMovesOutputDTO:
    valid_moves: list[dict[str, int]]
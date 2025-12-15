from dataclasses import dataclass

@dataclass(frozen=True)
class GetValidMovesOutputDTO:
    valid_moves: list[tuple[int, int]]
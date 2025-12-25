from dataclasses import dataclass

@dataclass(frozen=True)
class GetValidMovesOutput:
    valid_moves: list[dict[str, int]]
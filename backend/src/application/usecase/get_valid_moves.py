from uuid import UUID

from ...domain.repository import GameRepository
from ..dto import GetValidMovesInput, GetValidMovesOutput
from ..exception import GameNotFoundException


class GetValidMoves:
    def __init__(self, game_repository: GameRepository):
        self._game_repository = game_repository

    async def execute(self, input_dto: GetValidMovesInput) -> GetValidMovesOutput:
        game = await self._game_repository.find_by_id(UUID(input_dto.game_id))

        if game is None:
            raise GameNotFoundException(input_dto.game_id)

        valid_moves = [
            {"row": pos.row, "col": pos.col} for pos in game.get_valid_moves()
        ]

        return GetValidMovesOutput(valid_moves)

from uuid import UUID

from ..dto.get_valid_moves import GetValidMovesInputDTO, GetValidMovesOutputDTO
from ...domain.repository.game_repository import GameRepository


class GetValidMoves:
    def __init__(self, game_repository: GameRepository):
        self._game_repository = game_repository

    async def execute(self, input_dto: GetValidMovesInputDTO) -> GetValidMovesOutputDTO:
        game = await self._game_repository.find_by_id(UUID(input_dto.game_id))

        if game is None:
            raise ValueError(f"ゲームが見つかりません: {input_dto.game_id}")

        valid_moves = [
            {"row": pos.row, "col": pos.col}
            for pos in game.get_valid_moves()
        ]

        return GetValidMovesOutputDTO(valid_moves)
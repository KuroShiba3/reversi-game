from uuid import UUID

from ...domain.repository.game_repository import GameRepository
from ..dto.get_game_state import GetGameStateInput, GetGameStateOutput


class GetGameState:
    def __init__(self, game_repository: GameRepository):
        self._game_repository = game_repository

    async def execute(self, input_dto: GetGameStateInput) -> GetGameStateOutput:
        game = await self._game_repository.find_by_id(UUID(input_dto.game_id))

        if game is None:
            raise ValueError(f"ゲームが見つかりません: {input_dto.game_id}")

        board_state = [
            {"row": pos.row, "col": pos.col, "disc": disc.name}
            for pos, disc in game.board.cells.items()
        ]

        black_score, white_score = game.get_scores()

        return GetGameStateOutput(
            board_state,
            game.current_player.name,
            black_score,
            white_score,
            game.status.value
        )
from uuid import UUID

from ...domain.exception import GameAlreadyFinishedException
from ...domain.model import GameStatus
from ...domain.repository import GameRepository
from ..dto import PassTurnInput
from ..exception import GameNotFoundException


class PassTurn:
    def __init__(self, game_repository: GameRepository):
        self._game_repository = game_repository

    async def execute(self, input_dto: PassTurnInput) -> None:
        game = await self._game_repository.find_by_id(UUID(input_dto.game_id))

        if game is None:
            raise GameNotFoundException(input_dto.game_id)

        if game.status == GameStatus.FINISHED:
            raise GameAlreadyFinishedException(UUID(input_dto.game_id))

        game.pass_turn()

        if game.is_game_over():
            game.finish()

        # ゲームを保存
        await self._game_repository.save(game)

from uuid import UUID

from ...domain.exception import GameAlreadyFinishedException
from ...domain.model import GameStatus, Position
from ...domain.repository import GameRepository
from ..dto import PlaceDiscInput
from ..exception import GameNotFoundException


class PlaceDisc:
    def __init__(self, game_repository: GameRepository):
        self._game_repository = game_repository

    async def execute(self, input_dto: PlaceDiscInput) -> None:
        game = await self._game_repository.find_by_id(UUID(input_dto.game_id))

        if game is None:
            raise GameNotFoundException(input_dto.game_id)

        if game.status == GameStatus.FINISHED:
            raise GameAlreadyFinishedException(UUID(input_dto.game_id))

        position = Position(input_dto.position["row"], input_dto.position["col"])

        game.place_disc(position)

        if game.is_game_over():
            game.finish()

        await self._game_repository.save(game)

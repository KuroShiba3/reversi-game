from uuid import UUID

from ...domain.model import GameStatus, Position
from ...domain.repository import GameRepository
from ..dto.place_disc import PlaceDiscInput


class PlaceDisc:
    def __init__(self, game_repository: GameRepository):
        self._game_repository = game_repository

    async def execute(self, input_dto: PlaceDiscInput) -> None:
        game = await self._game_repository.find_by_id(UUID(input_dto.game_id))

        if game is None:
            raise ValueError(f"ゲームが見つかりません: {input_dto.game_id}")

        if game.status == GameStatus.FINISHED:
            raise ValueError("ゲームはすでに終了しています。")

        position = Position(input_dto.position["row"], input_dto.position["col"])

        game.place_disc(position)

        # ゲーム終了判定
        if game.is_game_over():
            game.finish()

        # ゲームを保存
        await self._game_repository.save(game)

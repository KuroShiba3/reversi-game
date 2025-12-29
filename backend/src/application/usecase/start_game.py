from uuid import UUID

from ...domain.model import Game
from ...domain.repository import GameRepository


class StartGame:
    """新しいゲームを開始するユースケース"""

    def __init__(self, game_repository: GameRepository):
        self._game_repository = game_repository

    async def execute(self) -> UUID:
        """新しいゲームを作成して保存し、ゲームIDを返す"""
        new_game = Game.create()
        await self._game_repository.save(new_game)
        return new_game.id

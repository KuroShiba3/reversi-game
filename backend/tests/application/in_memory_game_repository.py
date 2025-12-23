from uuid import UUID

from src.domain.model.game import Game
from src.domain.repository.game_repository import GameRepository


class InMemoryGameRepository(GameRepository):
    """テスト用のインメモリゲームリポジトリ"""

    def __init__(self):
        self._games: dict[UUID, Game] = {}

    async def save(self, game: Game) -> None:
        """ゲームを保存"""
        self._games[game.id] = game

    async def find_by_id(self, game_id: UUID) -> Game | None:
        """IDでゲームを検索"""
        return self._games.get(game_id)

    def clear(self) -> None:
        """全データをクリア（テスト用）"""
        self._games.clear()

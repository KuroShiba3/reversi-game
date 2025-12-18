from abc import ABC, abstractmethod
from uuid import UUID

from ..model.game import Game


class IGameRepository(ABC):
    @abstractmethod
    async def save(self, game: Game) -> None:
        """
        ゲームを保存（新規作成または更新）
        ゲームが終了している場合（game.result が存在する場合）は結果も保存
        """
        pass

    @abstractmethod
    async def find_by_id(self, game_id: UUID) -> Game | None:
        """IDでゲームを検索"""
        pass
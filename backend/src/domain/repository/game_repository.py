from typing import Protocol
from uuid import UUID

from ..model.game import Game


class GameRepository(Protocol):
    async def save(self, game: Game) -> None:
        """
        ゲームを保存（新規作成または更新）
        ゲームが終了している場合（game.result が存在する場合）は結果も保存
        """
        ...

    async def find_by_id(self, game_id: UUID) -> Game | None:
        """IDでゲームを検索"""
        ...
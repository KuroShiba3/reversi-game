from uuid import UUID

from ...domain.model import GameStatus
from ...domain.repository import GameRepository
from ..dto.pass_turn import PassTurnInput


class PassTurn:
    def __init__(self, game_repository: GameRepository):
        self._game_repository = game_repository

    async def execute(self, input_dto: PassTurnInput) -> None:
        game = await self._game_repository.find_by_id(UUID(input_dto.game_id))

        if game is None:
            raise ValueError(f"ゲームが見つかりません: {input_dto.game_id}")

        if game.status == GameStatus.FINISHED:
            raise ValueError("ゲームはすでに終了しています。")

        # 現在のプレイヤーが本当にパスする必要があるかチェック
        if game.can_current_player_move():
            raise ValueError("現在のプレイヤーは有効な手があるため、パスできません。")

        game.pass_turn()

        # パス後にゲーム終了判定
        if game.is_game_over():
            game.finish()

        # ゲームを保存
        await self._game_repository.save(game)

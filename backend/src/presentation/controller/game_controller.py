from ...application.dto import (
    GetGameStateInput,
    GetValidMovesInput,
    PassTurnInput,
    PlaceDiscInput,
)
from ...application.usecase import (
    GetGameState,
    GetValidMoves,
    PassTurn,
    PlaceDisc,
    StartGame,
)
from ...domain.repository import GameRepository
from ..schemas import (
    CellState,
    GameStateResponse,
    Position,
    StartGameResponse,
)


class GameController:
    """ゲーム関連のコントローラー"""

    def __init__(self, game_repository: GameRepository):
        self._game_repository = game_repository

    async def start_game(self) -> StartGameResponse:
        """新しいゲームを開始する"""
        usecase = StartGame(self._game_repository)
        game_id = await usecase.execute()

        state_result = await self._get_game_state_response(str(game_id))

        return StartGameResponse(
            game_id=str(game_id),
            board_state=state_result.board_state,
            current_player=state_result.current_player,
            black_score=state_result.black_score,
            white_score=state_result.white_score,
            status=state_result.status,
            valid_moves=state_result.valid_moves,
        )

    async def place_disc(self, game_id: str, row: int, col: int) -> GameStateResponse:
        """指定した位置に石を置く（現在のプレイヤーの石を配置）"""
        # 石を置く
        usecase = PlaceDisc(self._game_repository)
        await usecase.execute(
            PlaceDiscInput(
                game_id=game_id,
                position={"row": row, "col": col},
            )
        )

        return await self._get_game_state_response(game_id)

    async def pass_turn(self, game_id: str) -> GameStateResponse:
        """現在のプレイヤーのターンをパスする"""
        # パスを実行
        usecase = PassTurn(self._game_repository)
        await usecase.execute(PassTurnInput(game_id))

        return await self._get_game_state_response(game_id)

    async def _get_game_state_response(self, game_id: str) -> GameStateResponse:
        """ゲーム状態のレスポンスを取得する（内部メソッド）"""
        # ゲーム状態を取得
        state_usecase = GetGameState(self._game_repository)
        state_result = await state_usecase.execute(GetGameStateInput(game_id))

        # 有効手を取得
        moves_usecase = GetValidMoves(self._game_repository)
        moves_result = await moves_usecase.execute(GetValidMovesInput(game_id))

        board_state = [
            CellState(row=cell["row"], col=cell["col"], disc=cell["disc"])
            for cell in state_result.board_state
        ]

        valid_moves = [
            Position(row=move["row"], col=move["col"])
            for move in moves_result.valid_moves
        ]

        return GameStateResponse(
            board_state=board_state,
            current_player=state_result.current_player,
            black_score=state_result.black_score,
            white_score=state_result.white_score,
            status=state_result.status,
            valid_moves=valid_moves,
        )

from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

from .schemas import (
    StartGameResponse,
    GetGameStateResponse,
    GetValidMovesResponse,
    PlaceDiscRequest,
    CellState,
    Position,
)
from ..application.usecase.start_game import StartGame
from ..application.usecase.get_game_state import GetGameState
from ..application.usecase.get_valid_moves import GetValidMoves
from ..application.usecase.place_disc import PlaceDisc
from ..application.usecase.pass_turn import PassTurn
from ..application.dto.get_game_state import GetGameStateInput
from ..application.dto.get_valid_moves import GetValidMovesInput
from ..application.dto.place_disc import PlaceDiscInput
from ..application.dto.pass_turn import PassTurnInput
from ..infrastructure.database.connection_pool import DatabasePool
from ..infrastructure.repository.game_repository_impl import GameRepositoryImpl

router = APIRouter(prefix="/api/games", tags=["games"])


def get_game_repository() -> GameRepositoryImpl:
    """ゲームリポジトリの依存性注入"""
    pool = DatabasePool.get_pool()
    return GameRepositoryImpl(pool)


@router.post("", response_model=StartGameResponse, status_code=201)
async def start_game(
    game_repository: GameRepositoryImpl = Depends(get_game_repository),
):
    """新しいゲームを開始する"""
    try:
        usecase = StartGame(game_repository)
        result = await usecase.execute()

        board_state = [
            CellState(row=cell["row"], col=cell["col"], disc=cell["disc"])
            for cell in result.board_state
        ]

        return StartGameResponse(
            game_id=result.game_id,
            board_state=board_state,
            current_player=result.current_player,
            status=result.status,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{game_id}", response_model=GetGameStateResponse)
async def get_game_state(
    game_id: str,
    game_repository: GameRepositoryImpl = Depends(get_game_repository),
):
    """ゲームの現在の状態を取得する（デバッグ用・有効手含む）"""
    try:
        # ゲーム状態を取得
        state_usecase = GetGameState(game_repository)
        state_result = await state_usecase.execute(GetGameStateInput(game_id))

        # 有効手を取得
        moves_usecase = GetValidMoves(game_repository)
        moves_result = await moves_usecase.execute(GetValidMovesInput(game_id))

        board_state = [
            CellState(row=cell["row"], col=cell["col"], disc=cell["disc"])
            for cell in state_result.board_state
        ]

        valid_moves = [
            Position(row=move["row"], col=move["col"])
            for move in moves_result.valid_moves
        ]

        return GetGameStateResponse(
            board_state=board_state,
            current_player=state_result.current_player,
            black_score=state_result.black_score,
            white_score=state_result.white_score,
            status=state_result.status,
            valid_moves=valid_moves,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{game_id}/moves", response_model=GetValidMovesResponse)
async def get_valid_moves(
    game_id: str,
    game_repository: GameRepositoryImpl = Depends(get_game_repository),
):
    """現在のプレイヤーが置ける有効な手を取得する"""
    try:
        usecase = GetValidMoves(game_repository)
        result = await usecase.execute(GetValidMovesInput(game_id))

        valid_moves = [
            Position(row=move["row"], col=move["col"]) for move in result.valid_moves
        ]

        return GetValidMovesResponse(valid_moves=valid_moves)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{game_id}/moves", status_code=204)
async def place_disc(
    game_id: str,
    request: PlaceDiscRequest,
    game_repository: GameRepositoryImpl = Depends(get_game_repository),
):
    """指定した位置に石を置く"""
    try:
        # game_idからゲームを取得して現在のプレイヤーを判定
        state_usecase = GetGameState(game_repository)
        state_result = await state_usecase.execute(GetGameStateInput(game_id))

        usecase = PlaceDisc(game_repository)
        await usecase.execute(
            PlaceDiscInput(
                game_id=game_id,
                disc=state_result.current_player,
                position={"row": request.row, "col": request.col},
            )
        )
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{game_id}/pass", status_code=204)
async def pass_turn(
    game_id: str,
    game_repository: GameRepositoryImpl = Depends(get_game_repository),
):
    """現在のプレイヤーのターンをパスする"""
    try:
        usecase = PassTurn(game_repository)
        await usecase.execute(PassTurnInput(game_id))
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

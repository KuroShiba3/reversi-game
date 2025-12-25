from fastapi import APIRouter, HTTPException, Depends

from .schemas import StartGameResponse, GameStateResponse, PlaceDiscRequest
from .controller import GameController
from ..infrastructure.database.connection_pool import DatabasePool
from ..infrastructure.repository import GameRepositoryImpl

router = APIRouter(prefix="/api/games", tags=["games"])


def get_game_controller() -> GameController:
    """ゲームコントローラーの依存性注入"""
    pool = DatabasePool.get_pool()
    repository = GameRepositoryImpl(pool)
    return GameController(repository)


@router.post("", response_model=StartGameResponse, status_code=201)
async def start_game(
    controller: GameController = Depends(get_game_controller),
):
    """新しいゲームを開始する"""
    try:
        return await controller.start_game()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{game_id}/moves", response_model=GameStateResponse)
async def place_disc(
    game_id: str,
    request: PlaceDiscRequest,
    controller: GameController = Depends(get_game_controller),
):
    """指定した位置に石を置く"""
    try:
        return await controller.place_disc(game_id, request.row, request.col)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{game_id}/pass", response_model=GameStateResponse)
async def pass_turn(
    game_id: str,
    controller: GameController = Depends(get_game_controller),
):
    """現在のプレイヤーのターンをパスする"""
    try:
        return await controller.pass_turn(game_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

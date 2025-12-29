from fastapi import APIRouter, Depends, HTTPException, status

from ..application.exception import GameNotFoundException
from ..domain.exception import (
    CannotPassWithValidMovesException,
    GameAlreadyFinishedException,
    InvalidMoveException,
    InvalidPositionException,
)
from ..infrastructure.database.connection_pool import DatabasePool
from ..infrastructure.exception import RepositoryException
from ..infrastructure.repository import GameRepositoryImpl
from .controller import GameController
from .schemas import GameStateResponse, PlaceDiscRequest, StartGameResponse

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

    except GameNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "game_not_found", "game_id": e.game_id},
        )

    except InvalidPositionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_position",
                "row": e.row,
                "col": e.col,
                "message": str(e),
            },
        )

    except InvalidMoveException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_move",
                "row": e.row,
                "col": e.col,
                "disc": e.disc_name,
                "reason": e.reason,
            },
        )

    except GameAlreadyFinishedException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "game_already_finished", "game_id": str(e.game_id)},
        )

    except RepositoryException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "repository_error",
                "operation": e.operation,
                "message": str(e),
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": str(e),
            },
        )


@router.post("/{game_id}/pass", response_model=GameStateResponse)
async def pass_turn(
    game_id: str,
    controller: GameController = Depends(get_game_controller),
):
    """現在のプレイヤーのターンをパスする"""
    try:
        return await controller.pass_turn(game_id)

    except GameNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "game_not_found", "game_id": e.game_id},
        )

    except CannotPassWithValidMovesException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "cannot_pass_with_valid_moves",
                "player": e.current_player_name,
                "valid_moves_count": e.valid_moves_count,
                "message": str(e),
            },
        )

    except GameAlreadyFinishedException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "game_already_finished", "game_id": str(e.game_id)},
        )

    except RepositoryException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "repository_error",
                "operation": e.operation,
                "message": str(e),
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "internal_error",
                "message": str(e),
            },
        )

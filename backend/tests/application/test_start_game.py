import pytest
from uuid import UUID

from src.application.usecase import StartGame
from src.domain.model import Disc, GameStatus, Position

from tests.repository import InMemoryGameRepository


@pytest.fixture
def repository():
    return InMemoryGameRepository()


@pytest.fixture
def usecase(repository):
    return StartGame(repository)


async def test_start_game_creates_new_game(repository, usecase):
    """新しいゲームが作成される"""
    game_id = await usecase.execute()

    assert game_id is not None
    assert isinstance(game_id, UUID)

    saved_game = await repository.find_by_id(game_id)
    assert saved_game is not None
    assert saved_game.id == game_id


async def test_start_game_initial_state(repository, usecase):
    """初期状態が正しく設定される"""
    game_id = await usecase.execute()

    saved_game = await repository.find_by_id(game_id)
    assert saved_game.current_player == Disc.BLACK
    assert saved_game.status == GameStatus.PLAYING


async def test_start_game_initial_board_setup(repository, usecase):
    """初期盤面が正しくセットアップされる"""
    game_id = await usecase.execute()

    saved_game = await repository.find_by_id(game_id)
    board = saved_game.board

    # 中央4マスの初期配置を確認
    assert board.cells[Position(3, 3)] == Disc.WHITE
    assert board.cells[Position(3, 4)] == Disc.BLACK
    assert board.cells[Position(4, 3)] == Disc.BLACK
    assert board.cells[Position(4, 4)] == Disc.WHITE

    # 全マス数を確認（64マス全て）
    assert len(board.cells) == 64

    # 石が置かれているマス数を確認（EMPTYでないマス）
    non_empty_count = sum(1 for disc in board.cells.values() if disc != Disc.EMPTY)
    assert non_empty_count == 4
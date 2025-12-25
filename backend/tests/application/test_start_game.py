import pytest
from uuid import UUID

from src.application.usecase import StartGame
from src.domain.model import Disc, Position

from tests.repository import InMemoryGameRepository


@pytest.fixture
def repository():
    return InMemoryGameRepository()


@pytest.fixture
def usecase(repository):
    return StartGame(repository)


async def test_start_game_creates_new_game(repository, usecase):
    """新しいゲームが作成される"""
    result = await usecase.execute()

    assert result.game_id is not None
    game_id = UUID(result.game_id)

    saved_game = await repository.find_by_id(game_id)
    assert saved_game is not None
    assert saved_game.id == game_id


async def test_start_game_initial_state(usecase):
    """初期状態が正しく設定される"""
    result = await usecase.execute()

    assert result.current_player == "BLACK"
    assert result.status == "playing"

    assert len(result.board_state) == 64


async def test_start_game_initial_board_setup(usecase):
    """初期盤面が正しくセットアップされる"""
    result = await usecase.execute()

    board_dict = {(cell["row"], cell["col"]): cell["disc"] for cell in result.board_state}

    assert board_dict[(3, 3)] == "WHITE"
    assert board_dict[(3, 4)] == "BLACK"
    assert board_dict[(4, 3)] == "BLACK"
    assert board_dict[(4, 4)] == "WHITE"

    empty_count = sum(1 for cell in result.board_state if cell["disc"] == "EMPTY")
    assert empty_count == 60
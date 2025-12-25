import pytest
from uuid import uuid4

from src.application.dto.get_game_state import GetGameStateInput
from src.application.usecase import GetGameState
from src.domain.model import Game, Disc, Position

from tests.repository import InMemoryGameRepository


@pytest.fixture
def repository():
    return InMemoryGameRepository()


@pytest.fixture
def usecase(repository):
    return GetGameState(repository)


@pytest.mark.asyncio
async def test_get_game_state_initial(repository, usecase):
    """初期状態のゲーム状態取得テスト"""
    game = Game.create()
    await repository.save(game)

    input_dto = GetGameStateInput(str(game.id))
    output = await usecase.execute(input_dto)

    assert output.current_player == "BLACK"
    assert output.black_score == 2
    assert output.white_score == 2
    assert output.status == "playing"

    assert len(output.board_state) == 64

    board_dict = {(cell["row"], cell["col"]): cell["disc"] for cell in output.board_state}
    assert board_dict[(3, 3)] == "WHITE"
    assert board_dict[(3, 4)] == "BLACK"
    assert board_dict[(4, 3)] == "BLACK"
    assert board_dict[(4, 4)] == "WHITE"


@pytest.mark.asyncio
async def test_get_game_state_after_move(repository, usecase):
    """石を置いた後のゲーム状態取得テスト"""
    game = Game.create()
    game.place_disc(Position(2, 3), Disc.BLACK)
    await repository.save(game)

    input_dto = GetGameStateInput(str(game.id))
    output = await usecase.execute(input_dto)

    assert output.current_player == "WHITE"
    assert output.black_score == 4
    assert output.white_score == 1
    assert output.status == "playing"

    board_dict = {(cell["row"], cell["col"]): cell["disc"] for cell in output.board_state}
    assert board_dict[(2, 3)] == "BLACK"
    assert board_dict[(3, 3)] == "BLACK"


@pytest.mark.asyncio
async def test_get_game_state_finished_game(repository, usecase):
    """終了したゲームの状態取得テスト"""
    game = Game.create()
    game.place_disc(Position(2, 3), Disc.BLACK)
    game.finish()
    await repository.save(game)

    input_dto = GetGameStateInput(str(game.id))
    output = await usecase.execute(input_dto)

    assert output.status == "finished"
    assert output.black_score == 4
    assert output.white_score == 1


@pytest.mark.asyncio
async def test_get_game_state_game_not_found(repository, usecase):
    """存在しないゲームIDの場合はエラーが発生する"""
    non_existent_id = str(uuid4())

    input_dto = GetGameStateInput(non_existent_id)
    with pytest.raises(ValueError) as exc_info:
        await usecase.execute(input_dto)

    assert f"ゲームが見つかりません: {non_existent_id}" in str(exc_info.value)
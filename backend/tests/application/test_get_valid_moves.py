import pytest
from uuid import uuid4

from src.application.dto.get_valid_moves import GetValidMovesInput
from src.application.usecase import GetValidMoves
from src.application.exception import GameNotFoundException
from src.domain.model import Game, Disc, Position, GameStatus

from tests.repository import InMemoryGameRepository


@pytest.fixture
def repository():
    return InMemoryGameRepository()


@pytest.fixture
def usecase(repository):
    return GetValidMoves(repository)


async def test_get_valid_moves_initial(repository, usecase):
    """初期状態の有効手取得テスト"""
    game = Game.create()
    await repository.save(game)

    input_dto = GetValidMovesInput(str(game.id))
    output = await usecase.execute(input_dto)

    assert len(output.valid_moves) == 4

    positions = [(move["row"], move["col"]) for move in output.valid_moves]
    assert (2, 3) in positions
    assert (3, 2) in positions
    assert (4, 5) in positions
    assert (5, 4) in positions


async def test_get_valid_moves_after_move(repository, usecase):
    """石を置いた後の有効手取得テスト（白のターン）"""
    game = Game.create()
    game.place_disc(Position(2, 3))  # 黒が打つ -> 白のターンになる
    await repository.save(game)

    input_dto = GetValidMovesInput(str(game.id))
    output = await usecase.execute(input_dto)

    # 白の有効手が取得できる
    assert len(output.valid_moves) > 0
    assert output.valid_moves[0]["row"] >= 0
    assert output.valid_moves[0]["col"] >= 0


async def test_get_valid_moves_no_valid_moves(repository, usecase):
    """有効手がない場合のテスト"""
    cells = {}
    for row in range(8):
        for col in range(8):
            cells[Position(row, col)] = Disc.BLACK

    from src.domain.model.board import Board
    board = Board.reconstruct(cells)
    game = Game.reconstruct(uuid4(), board, Disc.WHITE, GameStatus.PLAYING)
    await repository.save(game)

    input_dto = GetValidMovesInput(str(game.id))
    output = await usecase.execute(input_dto)

    assert len(output.valid_moves) == 0
    assert output.valid_moves == []


async def test_get_valid_moves_finished_game(repository, usecase):
    """終了したゲームの有効手取得テスト"""
    game = Game.create()
    game.finish()
    await repository.save(game)

    input_dto = GetValidMovesInput(str(game.id))
    output = await usecase.execute(input_dto)

    assert len(output.valid_moves) == 0
    assert output.valid_moves == []


async def test_get_valid_moves_game_not_found(usecase):
    """存在しないゲームIDの場合はエラーが発生する"""
    non_existent_id = str(uuid4())

    input_dto = GetValidMovesInput(non_existent_id)
    with pytest.raises(GameNotFoundException) as exc_info:
        await usecase.execute(input_dto)

    assert f"ゲームが見つかりません: {non_existent_id}" in str(exc_info.value)
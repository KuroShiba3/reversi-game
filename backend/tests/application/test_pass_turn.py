import pytest
from uuid import uuid4

from src.application.dto.pass_turn import PassTurnInput
from src.application.usecase import PassTurn
from src.domain.model import Game, Disc, Position, GameStatus, Board

from tests.repository import InMemoryGameRepository


@pytest.fixture
def repository():
    return InMemoryGameRepository()


@pytest.fixture
def usecase(repository):
    return PassTurn(repository)


async def test_pass_turn_cannot_pass_with_valid_moves(repository, usecase):
    """有効な手がある場合、パスできない"""
    game = Game.create()
    await repository.save(game)

    assert game.can_current_player_move()
    assert len(game.get_valid_moves()) == 4

    input_dto = PassTurnInput(str(game.id))
    with pytest.raises(ValueError) as exc_info:
        await usecase.execute(input_dto)

    assert "現在のプレイヤーは有効な手があるため、パスできません。" in str(exc_info.value)


async def test_pass_turn_game_not_found(repository, usecase):
    """存在しないゲームIDの場合はエラーが発生する"""
    non_existent_id = str(uuid4())

    input_dto = PassTurnInput(non_existent_id)
    with pytest.raises(ValueError) as exc_info:
        await usecase.execute(input_dto)

    assert f"ゲームが見つかりません: {non_existent_id}" in str(exc_info.value)


async def test_pass_turn_finished_game(repository, usecase):
    """終了したゲームではパスできない"""
    game = Game.create()
    game.finish()
    await repository.save(game)

    input_dto = PassTurnInput(str(game.id))
    with pytest.raises(ValueError) as exc_info:
        await usecase.execute(input_dto)

    assert "ゲームはすでに終了しています。" in str(exc_info.value)


async def test_pass_turn_alternates_players(repository, usecase):
    """パスを繰り返すとプレイヤーが交互に切り替わる"""
    cells = {}
    for row in range(8):
        for col in range(8):
            cells[Position(row, col)] = Disc.BLACK

    board = Board.reconstruct(cells)
    game = Game.reconstruct(uuid4(), board, Disc.BLACK, GameStatus.PLAYING)
    await repository.save(game)

    assert not game.can_current_player_move()
    assert len(game.get_valid_moves()) == 0

    input_dto = PassTurnInput(str(game.id))
    await usecase.execute(input_dto)

    updated_game = await repository.find_by_id(game.id)
    assert updated_game.status == GameStatus.FINISHED


async def test_pass_turn_creates_game_result_when_finished(repository, usecase):
    """パス後にゲームが終了する場合、GameResultが作成される"""
    cells = {}
    for row in range(8):
        for col in range(8):
            if row < 4:
                cells[Position(row, col)] = Disc.BLACK
            else:
                cells[Position(row, col)] = Disc.WHITE

    board = Board.reconstruct(cells)
    game = Game.reconstruct(uuid4(), board, Disc.BLACK, GameStatus.PLAYING)
    await repository.save(game)

    input_dto = PassTurnInput(str(game.id))
    await usecase.execute(input_dto)

    updated_game = await repository.find_by_id(game.id)
    if updated_game.status == GameStatus.FINISHED:
        assert updated_game.result is not None
        assert updated_game.result.game_id == game.id
        assert updated_game.result.black_score >= 0
        assert updated_game.result.white_score >= 0
        assert updated_game.result.finished_at is not None



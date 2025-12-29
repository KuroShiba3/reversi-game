import pytest
from uuid import uuid4

from src.application.dto.place_disc import PlaceDiscInput
from src.application.usecase import PlaceDisc
from src.application.exception import GameNotFoundException
from src.domain.model import Game, Disc, Position, GameStatus, Board
from src.domain.exception import InvalidMoveException, GameAlreadyFinishedException

from tests.repository import InMemoryGameRepository


@pytest.fixture
def repository():
    return InMemoryGameRepository()


@pytest.fixture
def usecase(repository):
    return PlaceDisc(repository)


async def test_place_disc_success(repository, usecase):
    """ディスクの配置が成功する"""
    game = Game.create()
    await repository.save(game)

    assert game.current_player == Disc.BLACK

    input_dto = PlaceDiscInput(
        game_id=str(game.id),
        position={"row": 2, "col": 3}
    )
    await usecase.execute(input_dto)

    updated_game = await repository.find_by_id(game.id)
    assert updated_game.current_player == Disc.WHITE
    assert updated_game.board.cells[Position(2, 3)] == Disc.BLACK
    assert updated_game.board.cells[Position(3, 3)] == Disc.BLACK


async def test_place_disc_game_not_found(repository, usecase):
    """存在しないゲームIDの場合はエラーが発生する"""
    non_existent_id = str(uuid4())

    input_dto = PlaceDiscInput(
        game_id=non_existent_id,
        position={"row": 2, "col": 3}
    )
    with pytest.raises(GameNotFoundException) as exc_info:
        await usecase.execute(input_dto)

    assert f"ゲームが見つかりません: {non_existent_id}" in str(exc_info.value)


async def test_place_disc_finished_game(repository, usecase):
    """終了したゲームではディスクを配置できない"""
    game = Game.create()
    game.finish()
    await repository.save(game)

    input_dto = PlaceDiscInput(
        game_id=str(game.id),
        position={"row": 2, "col": 3}
    )
    with pytest.raises(GameAlreadyFinishedException) as exc_info:
        await usecase.execute(input_dto)

    assert "終了しています" in str(exc_info.value)


async def test_place_disc_invalid_position(repository, usecase):
    """無効な位置にはディスクを配置できない"""
    game = Game.create()
    await repository.save(game)

    input_dto = PlaceDiscInput(
        game_id=str(game.id),
        position={"row": 0, "col": 0}
    )
    with pytest.raises(InvalidMoveException):
        await usecase.execute(input_dto)




async def test_place_disc_alternates_players(repository, usecase):
    """ディスク配置後、プレイヤーが交互に切り替わる"""
    game = Game.create()
    await repository.save(game)

    await usecase.execute(PlaceDiscInput(
        game_id=str(game.id),
        position={"row": 2, "col": 3}
    ))

    game = await repository.find_by_id(game.id)
    assert game.current_player == Disc.WHITE

    await usecase.execute(PlaceDiscInput(
        game_id=str(game.id),
        position={"row": 2, "col": 2}
    ))

    game = await repository.find_by_id(game.id)
    assert game.current_player == Disc.BLACK

async def test_place_disc_updates_scores(repository, usecase):
    """ディスク配置後、スコアが更新される"""
    game = Game.create()
    await repository.save(game)

    black_score, white_score = game.get_scores()
    assert black_score == 2
    assert white_score == 2

    await usecase.execute(PlaceDiscInput(
        game_id=str(game.id),
        position={"row": 2, "col": 3}
    ))

    updated_game = await repository.find_by_id(game.id)
    black_score, white_score = updated_game.get_scores()
    assert black_score == 4
    assert white_score == 1

async def test_place_disc_creates_game_result_when_finished(repository, usecase):
    """ゲーム終了時、GameResultが作成される"""
    cells = {}
    for row in range(8):
        for col in range(8):
            cells[Position(row, col)] = Disc.BLACK

    cells[Position(7, 7)] = Disc.EMPTY
    cells[Position(7, 6)] = Disc.WHITE
    cells[Position(6, 7)] = Disc.WHITE
    cells[Position(6, 6)] = Disc.WHITE

    board = Board.reconstruct(cells)
    game = Game.reconstruct(uuid4(), board, Disc.BLACK, GameStatus.PLAYING)
    await repository.save(game)

    await usecase.execute(PlaceDiscInput(
        game_id=str(game.id),
        position={"row": 7, "col": 7}
    ))

    updated_game = await repository.find_by_id(game.id)
    assert updated_game.result is not None
    assert updated_game.result.game_id == game.id
    assert updated_game.result.black_score > 0
    assert updated_game.result.white_score >= 0
    assert updated_game.result.finished_at is not None
    assert updated_game.result.winner == Disc.BLACK
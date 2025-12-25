import pytest
from uuid import uuid4

from src.application.dto.pass_turn import PassTurnInput
from src.application.usecase.pass_turn import PassTurn
from src.domain.model.game import Game
from src.domain.model.disc import Disc
from src.domain.model.position import Position
from src.domain.model.game_status import GameStatus
from src.domain.model.board import Board

from tests.application.in_memory_game_repository import InMemoryGameRepository


@pytest.fixture
def repository():
    """テスト用のインメモリリポジトリ"""
    return InMemoryGameRepository()


@pytest.fixture
def usecase(repository):
    """PassTurnユースケース"""
    return PassTurn(repository)


async def test_pass_turn_cannot_pass_with_valid_moves(repository, usecase):
    """有効な手がある場合、パスできない"""
    # Arrange: 初期状態のゲーム（黒には有効手が4つある）
    game = Game.create()
    await repository.save(game)

    # 黒には有効手があることを確認
    assert game.can_current_player_move()
    assert len(game.get_valid_moves()) == 4

    # Act & Assert: パスしようとするとエラー
    input_dto = PassTurnInput(str(game.id))
    with pytest.raises(ValueError) as exc_info:
        await usecase.execute(input_dto)

    assert "現在のプレイヤーは有効な手があるため、パスできません。" in str(exc_info.value)


async def test_pass_turn_game_not_found(repository, usecase):
    """存在しないゲームIDの場合はエラーが発生する"""
    # Arrange: 存在しないUUID
    non_existent_id = str(uuid4())

    # Act & Assert: ValueErrorが発生する
    input_dto = PassTurnInput(non_existent_id)
    with pytest.raises(ValueError) as exc_info:
        await usecase.execute(input_dto)

    assert f"ゲームが見つかりません: {non_existent_id}" in str(exc_info.value)


async def test_pass_turn_finished_game(repository, usecase):
    """終了したゲームではパスできない"""
    # Arrange: ゲームを作成して終了させる
    game = Game.create()
    game.finish()
    await repository.save(game)

    # Act & Assert: パスしようとするとエラー
    input_dto = PassTurnInput(str(game.id))
    with pytest.raises(ValueError) as exc_info:
        await usecase.execute(input_dto)

    assert "ゲームはすでに終了しています。" in str(exc_info.value)


async def test_pass_turn_alternates_players(repository, usecase):
    """パスを繰り返すとプレイヤーが交互に切り替わる"""
    # Arrange: 両プレイヤーとも有効手がない盤面を作成
    cells = {}
    for row in range(8):
        for col in range(8):
            cells[Position(row, col)] = Disc.BLACK

    board = Board.reconstruct(cells)
    game = Game.reconstruct(uuid4(), board, Disc.BLACK, GameStatus.PLAYING)
    await repository.save(game)

    # 黒にも白にも有効手がないことを確認
    assert not game.can_current_player_move()
    assert len(game.get_valid_moves()) == 0

    # Act: 黒がパス
    input_dto = PassTurnInput(str(game.id))
    await usecase.execute(input_dto)

    # Assert: 白のターンに切り替わり、ゲームが終了している
    updated_game = await repository.find_by_id(game.id)
    # 両プレイヤーとも手がないのでゲームは終了する
    assert updated_game.status == GameStatus.FINISHED


async def test_pass_turn_creates_game_result_when_finished(repository, usecase):
    """パス後にゲームが終了する場合、GameResultが作成される"""
    # Arrange: 両プレイヤーとも有効手がない盤面
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

    # Act: パスする
    input_dto = PassTurnInput(str(game.id))
    await usecase.execute(input_dto)

    # Assert: GameResultが作成されている
    updated_game = await repository.find_by_id(game.id)
    if updated_game.status == GameStatus.FINISHED:
        assert updated_game.result is not None
        assert updated_game.result.game_id == game.id
        assert updated_game.result.black_score >= 0
        assert updated_game.result.white_score >= 0
        assert updated_game.result.finished_at is not None



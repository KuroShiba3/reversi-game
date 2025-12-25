import pytest
from uuid import uuid4

from src.application.dto.get_valid_moves import GetValidMovesInput
from src.application.usecase.get_valid_moves import GetValidMoves
from src.domain.model.game import Game
from src.domain.model.disc import Disc
from src.domain.model.position import Position
from src.domain.model.game_status import GameStatus

from tests.application.in_memory_game_repository import InMemoryGameRepository


@pytest.fixture
def repository():
    """テスト用のインメモリリポジトリ"""
    return InMemoryGameRepository()


@pytest.fixture
def usecase(repository):
    """GetValidMovesユースケース"""
    return GetValidMoves(repository)


async def test_get_valid_moves_initial(repository, usecase):
    """初期状態の有効手取得テスト"""
    # Arrange: 新規ゲームを作成して保存
    game = Game.create()
    await repository.save(game)

    # Act: 有効手を取得
    input_dto = GetValidMovesInput(str(game.id))
    output = await usecase.execute(input_dto)

    # Assert: 初期状態では黒の有効手が4つ
    assert len(output.valid_moves) == 4

    # 有効手の座標を確認
    positions = [(move["row"], move["col"]) for move in output.valid_moves]
    assert (2, 3) in positions
    assert (3, 2) in positions
    assert (4, 5) in positions
    assert (5, 4) in positions


async def test_get_valid_moves_after_move(repository, usecase):
    """石を置いた後の有効手取得テスト"""
    # Arrange: ゲームを作成し、黒が石を置く
    game = Game.create()
    game.place_disc(Position(2, 3), Disc.BLACK)
    await repository.save(game)

    # Act: 有効手を取得（白のターン）
    input_dto = GetValidMovesInput(str(game.id))
    output = await usecase.execute(input_dto)

    # Assert: 白の有効手が返される
    assert len(output.valid_moves) > 0
    assert output.valid_moves[0]["row"] >= 0
    assert output.valid_moves[0]["col"] >= 0


async def test_get_valid_moves_no_valid_moves(repository, usecase):
    """有効手がない場合のテスト"""
    # Arrange: 全てのマスが埋まっている盤面を作成
    cells = {}
    for row in range(8):
        for col in range(8):
            cells[Position(row, col)] = Disc.BLACK

    from src.domain.model.board import Board
    board = Board.reconstruct(cells)
    game = Game.reconstruct(uuid4(), board, Disc.WHITE, GameStatus.PLAYING)
    await repository.save(game)

    # Act: 有効手を取得
    input_dto = GetValidMovesInput(str(game.id))
    output = await usecase.execute(input_dto)

    # Assert: 有効手が空リスト
    assert len(output.valid_moves) == 0
    assert output.valid_moves == []


async def test_get_valid_moves_finished_game(repository, usecase):
    """終了したゲームの有効手取得テスト"""
    # Arrange: ゲームを作成して終了させる
    game = Game.create()
    game.finish()
    await repository.save(game)

    # Act: 有効手を取得
    input_dto = GetValidMovesInput(str(game.id))
    output = await usecase.execute(input_dto)

    # Assert: 終了したゲームでは有効手が空リスト
    assert len(output.valid_moves) == 0
    assert output.valid_moves == []


async def test_get_valid_moves_game_not_found(repository, usecase):
    """存在しないゲームIDの場合はエラーが発生する"""
    # Arrange: 存在しないUUID
    non_existent_id = str(uuid4())

    # Act & Assert: ValueErrorが発生する
    input_dto = GetValidMovesInput(non_existent_id)
    with pytest.raises(ValueError) as exc_info:
        await usecase.execute(input_dto)

    assert f"ゲームが見つかりません: {non_existent_id}" in str(exc_info.value)


async def test_get_valid_moves_output_format(repository, usecase):
    """有効手の出力形式が正しいことを確認"""
    # Arrange
    game = Game.create()
    await repository.save(game)

    # Act
    input_dto = GetValidMovesInput(str(game.id))
    output = await usecase.execute(input_dto)

    # Assert: 各有効手の形式を確認
    for move in output.valid_moves:
        assert "row" in move
        assert "col" in move
        assert isinstance(move["row"], int)
        assert isinstance(move["col"], int)
        assert 0 <= move["row"] <= 7
        assert 0 <= move["col"] <= 7


async def test_get_valid_moves_changes_with_game_state(repository, usecase):
    """ゲーム状態によって有効手が変わることを確認"""
    # Arrange: 新規ゲーム
    game = Game.create()
    await repository.save(game)

    # Act: 初期状態の有効手
    input_dto = GetValidMovesInput(str(game.id))
    output1 = await usecase.execute(input_dto)
    initial_moves = set((m["row"], m["col"]) for m in output1.valid_moves)

    # 黒が石を置く
    game.place_disc(Position(2, 3), Disc.BLACK)
    await repository.save(game)

    # Act: 石を置いた後の有効手（白のターン）
    output2 = await usecase.execute(input_dto)
    after_move_positions = set((m["row"], m["col"]) for m in output2.valid_moves)

    # Assert: 有効手が変わっている（黒のターン vs 白のターン）
    assert initial_moves != after_move_positions


async def test_get_valid_moves_multiple_games(repository, usecase):
    """複数のゲームで正しい有効手が取得できる"""
    # Arrange: 2つのゲームを作成
    game1 = Game.create()
    game2 = Game.create()
    game2.place_disc(Position(2, 3), Disc.BLACK)  # game2だけ石を置く

    await repository.save(game1)
    await repository.save(game2)

    # Act: game1の有効手（黒のターン）
    output1 = await usecase.execute(GetValidMovesInput(str(game1.id)))

    # Act: game2の有効手（白のターン）
    output2 = await usecase.execute(GetValidMovesInput(str(game2.id)))

    # Assert: それぞれ異なるプレイヤーの有効手が返される
    moves1 = set((m["row"], m["col"]) for m in output1.valid_moves)
    moves2 = set((m["row"], m["col"]) for m in output2.valid_moves)

    # 黒と白では有効手が異なる
    assert moves1 != moves2
    assert len(output1.valid_moves) > 0
    assert len(output2.valid_moves) > 0

import pytest
from uuid import uuid4

from src.application.dto.place_disc import PlaceDiscInput
from src.application.usecase import PlaceDisc
from src.domain.model import Game, Disc, Position, GameStatus, Board

from tests.application.in_memory_game_repository import InMemoryGameRepository


@pytest.fixture
def repository():
    """テスト用のインメモリリポジトリ"""
    return InMemoryGameRepository()


@pytest.fixture
def usecase(repository):
    """PlaceDiscユースケース"""
    return PlaceDisc(repository)


async def test_place_disc_success(repository, usecase):
    """ディスクの配置が成功する"""
    # Arrange: 初期状態のゲーム
    game = Game.create()
    await repository.save(game)

    # 黒のターン、有効な手の1つは(2, 3)
    assert game.current_player == Disc.BLACK

    # Act: 黒がディスクを配置
    input_dto = PlaceDiscInput(
        game_id=str(game.id),
        disc="BLACK",
        position={"row": 2, "col": 3}
    )
    await usecase.execute(input_dto)

    # Assert: ゲームの状態が更新されている
    updated_game = await repository.find_by_id(game.id)
    assert updated_game.current_player == Disc.WHITE  # ターンが切り替わっている
    assert updated_game.board.cells[Position(2, 3)] == Disc.BLACK  # 石が置かれている
    assert updated_game.board.cells[Position(3, 3)] == Disc.BLACK  # 白が黒に裏返っている


async def test_place_disc_game_not_found(repository, usecase):
    """存在しないゲームIDの場合はエラーが発生する"""
    # Arrange: 存在しないUUID
    non_existent_id = str(uuid4())

    # Act & Assert: ValueErrorが発生する
    input_dto = PlaceDiscInput(
        game_id=non_existent_id,
        disc="BLACK",
        position={"row": 2, "col": 3}
    )
    with pytest.raises(ValueError) as exc_info:
        await usecase.execute(input_dto)

    assert f"ゲームが見つかりません: {non_existent_id}" in str(exc_info.value)


async def test_place_disc_finished_game(repository, usecase):
    """終了したゲームではディスクを配置できない"""
    # Arrange: ゲームを作成して終了させる
    game = Game.create()
    game.finish()
    await repository.save(game)

    # Act & Assert: ValueErrorが発生する
    input_dto = PlaceDiscInput(
        game_id=str(game.id),
        disc="BLACK",
        position={"row": 2, "col": 3}
    )
    with pytest.raises(ValueError) as exc_info:
        await usecase.execute(input_dto)

    assert "ゲームはすでに終了しています。" in str(exc_info.value)


async def test_place_disc_invalid_position(repository, usecase):
    """無効な位置にはディスクを配置できない"""
    # Arrange: 初期状態のゲーム
    game = Game.create()
    await repository.save(game)

    # Act & Assert: 無効な位置(0, 0)に置こうとするとエラー
    input_dto = PlaceDiscInput(
        game_id=str(game.id),
        disc="BLACK",
        position={"row": 0, "col": 0}
    )
    with pytest.raises(ValueError):
        await usecase.execute(input_dto)


async def test_place_disc_wrong_player(repository, usecase):
    """現在のプレイヤーでない色のディスクは配置できない"""
    # Arrange: 初期状態のゲーム（黒のターン）
    game = Game.create()
    await repository.save(game)

    # Act & Assert: 白のディスクを置こうとするとエラー
    input_dto = PlaceDiscInput(
        game_id=str(game.id),
        disc="WHITE",
        position={"row": 2, "col": 3}
    )
    with pytest.raises(ValueError):
        await usecase.execute(input_dto)


async def test_place_disc_alternates_players(repository, usecase):
    """ディスク配置後、プレイヤーが交互に切り替わる"""
    # Arrange: 初期状態のゲーム
    game = Game.create()
    await repository.save(game)

    # Act: 黒がディスクを配置
    await usecase.execute(PlaceDiscInput(
        game_id=str(game.id),
        disc="BLACK",
        position={"row": 2, "col": 3}
    ))

    # Assert: 白のターンになっている
    game = await repository.find_by_id(game.id)
    assert game.current_player == Disc.WHITE

    # Act: 白がディスクを配置
    await usecase.execute(PlaceDiscInput(
        game_id=str(game.id),
        disc="WHITE",
        position={"row": 2, "col": 2}
    ))

    # Assert: 黒のターンに戻っている
    game = await repository.find_by_id(game.id)
    assert game.current_player == Disc.BLACK


async def test_place_disc_flips_opponent_discs(repository, usecase):
    """ディスク配置時、相手のディスクが正しく裏返る"""
    # Arrange: 初期状態のゲーム
    game = Game.create()
    await repository.save(game)

    # 初期状態: (3,3)は白
    assert game.board.cells[Position(3, 3)] == Disc.WHITE

    # Act: 黒が(2,3)に配置
    await usecase.execute(PlaceDiscInput(
        game_id=str(game.id),
        disc="BLACK",
        position={"row": 2, "col": 3}
    ))

    # Assert: (3,3)が黒に裏返っている
    updated_game = await repository.find_by_id(game.id)
    assert updated_game.board.cells[Position(3, 3)] == Disc.BLACK


async def test_place_disc_updates_scores(repository, usecase):
    """ディスク配置後、スコアが更新される"""
    # Arrange: 初期状態のゲーム
    game = Game.create()
    await repository.save(game)

    # 初期スコア
    black_score, white_score = game.get_scores()
    assert black_score == 2
    assert white_score == 2

    # Act: 黒が(2,3)に配置
    await usecase.execute(PlaceDiscInput(
        game_id=str(game.id),
        disc="BLACK",
        position={"row": 2, "col": 3}
    ))

    # Assert: スコアが更新されている
    updated_game = await repository.find_by_id(game.id)
    black_score, white_score = updated_game.get_scores()
    assert black_score == 4  # 2 + 置いた石1 + 裏返した石1
    assert white_score == 1  # 2 - 裏返された石1


async def test_place_disc_triggers_game_over(repository, usecase):
    """ディスク配置後、ゲームが終了する場合がある"""
    # Arrange: ほぼ全てのマスが埋まっている盤面を作成
    cells = {}
    for row in range(8):
        for col in range(8):
            cells[Position(row, col)] = Disc.BLACK

    # 最後の1マスだけ空ける
    cells[Position(7, 7)] = Disc.EMPTY
    # その隣に白を配置（黒が(7,7)に置ける）
    cells[Position(7, 6)] = Disc.WHITE
    cells[Position(6, 7)] = Disc.WHITE
    cells[Position(6, 6)] = Disc.WHITE

    board = Board.reconstruct(cells)
    game = Game.reconstruct(uuid4(), board, Disc.BLACK, GameStatus.PLAYING)
    await repository.save(game)

    # Act: 黒が最後のマスに配置
    await usecase.execute(PlaceDiscInput(
        game_id=str(game.id),
        disc="BLACK",
        position={"row": 7, "col": 7}
    ))

    # Assert: ゲームが終了している
    updated_game = await repository.find_by_id(game.id)
    assert updated_game.status == GameStatus.FINISHED
    assert updated_game.result is not None


async def test_place_disc_creates_game_result_when_finished(repository, usecase):
    """ゲーム終了時、GameResultが作成される"""
    # Arrange: 終了間近の盤面
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

    # Act: 最後の手を打つ
    await usecase.execute(PlaceDiscInput(
        game_id=str(game.id),
        disc="BLACK",
        position={"row": 7, "col": 7}
    ))

    # Assert: GameResultが作成されている
    updated_game = await repository.find_by_id(game.id)
    assert updated_game.result is not None
    assert updated_game.result.game_id == game.id
    assert updated_game.result.black_score > 0
    assert updated_game.result.white_score >= 0
    assert updated_game.result.finished_at is not None
    assert updated_game.result.winner == Disc.BLACK  # 黒が多い


async def test_place_disc_no_return_value(repository, usecase):
    """PlaceDiscは戻り値がない（None）"""
    # Arrange: 初期状態のゲーム
    game = Game.create()
    await repository.save(game)

    # Act
    input_dto = PlaceDiscInput(
        game_id=str(game.id),
        disc="BLACK",
        position={"row": 2, "col": 3}
    )
    result = await usecase.execute(input_dto)

    # Assert: 戻り値はNone
    assert result is None


async def test_place_disc_saves_game_state(repository, usecase):
    """ディスク配置後のゲーム状態が正しく保存される"""
    # Arrange: 初期状態のゲーム
    game = Game.create()
    game_id = game.id
    await repository.save(game)

    # Act: ディスクを配置
    await usecase.execute(PlaceDiscInput(
        game_id=str(game_id),
        disc="BLACK",
        position={"row": 2, "col": 3}
    ))

    # Assert: リポジトリから取得したゲームの状態が更新されている
    updated_game = await repository.find_by_id(game_id)
    assert updated_game is not None
    assert updated_game.current_player == Disc.WHITE
    assert updated_game.board.cells[Position(2, 3)] == Disc.BLACK

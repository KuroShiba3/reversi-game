import pytest
from uuid import UUID

from src.application.usecase import StartGame
from src.domain.model import Disc, Position

from tests.application.in_memory_game_repository import InMemoryGameRepository


@pytest.fixture
def repository():
    """テスト用のインメモリリポジトリ"""
    return InMemoryGameRepository()


@pytest.fixture
def usecase(repository):
    """StartGameユースケース"""
    return StartGame(repository)


async def test_start_game_creates_new_game(repository, usecase):
    """新しいゲームが作成される"""
    # Act: 新規ゲームを開始
    result = await usecase.execute()

    # Assert: ゲームIDが返される
    assert result.game_id is not None
    game_id = UUID(result.game_id)  # UUIDとしてパース可能

    # リポジトリに保存されている
    saved_game = await repository.find_by_id(game_id)
    assert saved_game is not None
    assert saved_game.id == game_id


async def test_start_game_initial_state(repository, usecase):
    """初期状態が正しく設定される"""
    # Act: 新規ゲームを開始
    result = await usecase.execute()

    # Assert: 初期状態が正しい
    assert result.current_player == "BLACK"  # 黒が先攻
    assert result.status == "playing"  # ゲームは進行中

    # ボード状態が64マス（8x8）
    assert len(result.board_state) == 64


async def test_start_game_initial_board_setup(repository, usecase):
    """初期盤面が正しくセットアップされる"""
    # Act: 新規ゲームを開始
    result = await usecase.execute()

    # Assert: 初期配置の4つの石を確認
    board_dict = {(cell["row"], cell["col"]): cell["disc"] for cell in result.board_state}

    # 中央4マスの配置
    assert board_dict[(3, 3)] == "WHITE"
    assert board_dict[(3, 4)] == "BLACK"
    assert board_dict[(4, 3)] == "BLACK"
    assert board_dict[(4, 4)] == "WHITE"

    # その他のマスは空
    empty_count = sum(1 for cell in result.board_state if cell["disc"] == "EMPTY")
    assert empty_count == 60  # 64 - 4 = 60マスが空


async def test_start_game_board_state_format(repository, usecase):
    """board_stateの形式が正しい"""
    # Act: 新規ゲームを開始
    result = await usecase.execute()

    # Assert: 各セルの形式を確認
    for cell in result.board_state:
        assert "row" in cell
        assert "col" in cell
        assert "disc" in cell
        assert isinstance(cell["row"], int)
        assert isinstance(cell["col"], int)
        assert isinstance(cell["disc"], str)
        assert 0 <= cell["row"] <= 7
        assert 0 <= cell["col"] <= 7
        assert cell["disc"] in ["EMPTY", "BLACK", "WHITE"]


async def test_start_game_saves_to_repository(repository, usecase):
    """ゲームがリポジトリに保存される"""
    # Act: 新規ゲームを開始
    result = await usecase.execute()

    # Assert: リポジトリから取得できる
    game_id = UUID(result.game_id)
    saved_game = await repository.find_by_id(game_id)

    assert saved_game is not None
    assert saved_game.current_player == Disc.BLACK
    assert saved_game.board.cells[Position(3, 3)] == Disc.WHITE
    assert saved_game.board.cells[Position(3, 4)] == Disc.BLACK
    assert saved_game.board.cells[Position(4, 3)] == Disc.BLACK
    assert saved_game.board.cells[Position(4, 4)] == Disc.WHITE


async def test_start_game_multiple_games(repository, usecase):
    """複数のゲームを作成できる"""
    # Act: 3つのゲームを開始
    result1 = await usecase.execute()
    result2 = await usecase.execute()
    result3 = await usecase.execute()

    # Assert: それぞれ異なるゲームIDを持つ
    assert result1.game_id != result2.game_id
    assert result2.game_id != result3.game_id
    assert result1.game_id != result3.game_id

    # すべてリポジトリに保存されている
    game1 = await repository.find_by_id(UUID(result1.game_id))
    game2 = await repository.find_by_id(UUID(result2.game_id))
    game3 = await repository.find_by_id(UUID(result3.game_id))

    assert game1 is not None
    assert game2 is not None
    assert game3 is not None


async def test_start_game_returns_output_dto(repository, usecase):
    """StartGameOutputを返す"""
    # Act: 新規ゲームを開始
    result = await usecase.execute()

    # Assert: Outputの型を確認
    from src.application.dto.start_game import StartGameOutput
    assert isinstance(result, StartGameOutput)

    # 必須フィールドが存在する
    assert hasattr(result, "game_id")
    assert hasattr(result, "board_state")
    assert hasattr(result, "current_player")
    assert hasattr(result, "status")


async def test_start_game_no_input_required(repository, usecase):
    """入力DTOなしで実行できる"""
    # Act: 引数なしで実行
    result = await usecase.execute()

    # Assert: 正常に実行される
    assert result is not None
    assert result.game_id is not None


async def test_start_game_consistent_state(repository, usecase):
    """DTOとリポジトリのゲームの状態が一致する"""
    # Act: 新規ゲームを開始
    result = await usecase.execute()

    # Assert: DTOの情報とリポジトリのゲームが一致
    game_id = UUID(result.game_id)
    saved_game = await repository.find_by_id(game_id)

    assert result.current_player == saved_game.current_player.name
    assert result.status == saved_game.status.value

    # ボード状態も一致
    for cell in result.board_state:
        pos = Position(cell["row"], cell["col"])
        expected_disc = saved_game.board.cells[pos].name
        assert cell["disc"] == expected_disc


async def test_start_game_initial_scores(repository, usecase):
    """初期スコアが2-2である"""
    # Act: 新規ゲームを開始
    result = await usecase.execute()

    # Assert: リポジトリからゲームを取得してスコアを確認
    game_id = UUID(result.game_id)
    saved_game = await repository.find_by_id(game_id)

    black_score, white_score = saved_game.get_scores()
    assert black_score == 2
    assert white_score == 2

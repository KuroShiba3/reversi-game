import pytest
from uuid import uuid4

from src.application.dto.get_game_state import GetGameStateInputDTO
from src.application.usecase.get_game_state import GetGameState
from src.domain.model.game import Game
from src.domain.model.disc import Disc
from src.domain.model.position import Position

from tests.application.in_memory_game_repository import InMemoryGameRepository


@pytest.fixture
def repository():
    """テスト用のインメモリリポジトリ"""
    return InMemoryGameRepository()


@pytest.fixture
def usecase(repository):
    """GetGameStateユースケース"""
    return GetGameState(repository)


@pytest.mark.asyncio
async def test_get_game_state_initial(repository, usecase):
    """初期状態のゲーム状態取得テスト"""
    # Arrange: 新規ゲームを作成して保存
    game = Game.create()
    await repository.save(game)

    # Act: ゲーム状態を取得
    input_dto = GetGameStateInputDTO(str(game.id))
    output = await usecase.execute(input_dto)

    # Assert: 初期状態が正しく返される
    assert output.current_player == "BLACK"
    assert output.black_score == 2
    assert output.white_score == 2
    assert output.status == "playing"

    # ボード状態の確認（初期配置4つの石）
    assert len(output.board_state) == 64  # 8x8のすべてのマス

    # 初期配置の石を確認
    board_dict = {(cell["row"], cell["col"]): cell["disc"] for cell in output.board_state}
    assert board_dict[(3, 3)] == "WHITE"
    assert board_dict[(3, 4)] == "BLACK"
    assert board_dict[(4, 3)] == "BLACK"
    assert board_dict[(4, 4)] == "WHITE"


@pytest.mark.asyncio
async def test_get_game_state_after_move(repository, usecase):
    """石を置いた後のゲーム状態取得テスト"""
    # Arrange: ゲームを作成し、黒が石を置く
    game = Game.create()
    game.place_disc(Position(2, 3), Disc.BLACK)
    await repository.save(game)

    # Act: ゲーム状態を取得
    input_dto = GetGameStateInputDTO(str(game.id))
    output = await usecase.execute(input_dto)

    # Assert: 石を置いた後の状態が正しく返される
    assert output.current_player == "WHITE"  # ターンが切り替わっている
    assert output.black_score == 4  # 2 + 置いた石1 + 裏返した石1
    assert output.white_score == 1  # 2 - 裏返された石1
    assert output.status == "playing"

    # 置いた石が反映されている
    board_dict = {(cell["row"], cell["col"]): cell["disc"] for cell in output.board_state}
    assert board_dict[(2, 3)] == "BLACK"
    assert board_dict[(3, 3)] == "BLACK"  # 裏返った


@pytest.mark.asyncio
async def test_get_game_state_finished_game(repository, usecase):
    """終了したゲームの状態取得テスト"""
    # Arrange: ゲームを作成して終了させる
    game = Game.create()
    game.place_disc(Position(2, 3), Disc.BLACK)  # 黒が優勢にする
    game.finish()
    await repository.save(game)

    # Act: ゲーム状態を取得
    input_dto = GetGameStateInputDTO(str(game.id))
    output = await usecase.execute(input_dto)

    # Assert: 終了状態が正しく返される
    assert output.status == "finished"
    assert output.black_score == 4
    assert output.white_score == 1


@pytest.mark.asyncio
async def test_get_game_state_game_not_found(repository, usecase):
    """存在しないゲームIDの場合はエラーが発生する"""
    # Arrange: 存在しないUUID
    non_existent_id = str(uuid4())

    # Act & Assert: ValueErrorが発生する
    input_dto = GetGameStateInputDTO(non_existent_id)
    with pytest.raises(ValueError) as exc_info:
        await usecase.execute(input_dto)

    assert f"ゲームが見つかりません: {non_existent_id}" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_game_state_board_state_format(repository, usecase):
    """board_stateの形式が正しいことを確認"""
    # Arrange
    game = Game.create()
    await repository.save(game)

    # Act
    input_dto = GetGameStateInputDTO(str(game.id))
    output = await usecase.execute(input_dto)

    # Assert: 各セルの形式を確認
    for cell in output.board_state:
        assert "row" in cell
        assert "col" in cell
        assert "disc" in cell
        assert isinstance(cell["row"], int)
        assert isinstance(cell["col"], int)
        assert isinstance(cell["disc"], str)
        assert 0 <= cell["row"] <= 7
        assert 0 <= cell["col"] <= 7
        assert cell["disc"] in ["EMPTY", "BLACK", "WHITE"]


@pytest.mark.asyncio
async def test_get_game_state_multiple_games(repository, usecase):
    """複数のゲームが保存されている場合、正しいゲームが取得できる"""
    # Arrange: 2つのゲームを作成
    game1 = Game.create()
    game2 = Game.create()
    game2.place_disc(Position(2, 3), Disc.BLACK)  # game2だけ石を置く

    await repository.save(game1)
    await repository.save(game2)

    # Act: game1を取得
    output1 = await usecase.execute(GetGameStateInputDTO(str(game1.id)))

    # Assert: game1は初期状態
    assert output1.current_player == "BLACK"
    assert output1.black_score == 2
    assert output1.white_score == 2

    # Act: game2を取得
    output2 = await usecase.execute(GetGameStateInputDTO(str(game2.id)))

    # Assert: game2は石を置いた後
    assert output2.current_player == "WHITE"
    assert output2.black_score == 4
    assert output2.white_score == 1

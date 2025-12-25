import pytest
from uuid import UUID

from src.presentation.controller import GameController
from src.presentation.schemas import (
    StartGameResponse,
    GameStateResponse,
    CellState,
    Position,
)
from src.domain.model import Game, Disc, Position as DomainPosition

from tests.repository import InMemoryGameRepository


@pytest.fixture
def repository():
    """テスト用のインメモリリポジトリ"""
    return InMemoryGameRepository()


@pytest.fixture
def controller(repository):
    """GameController"""
    return GameController(repository)


@pytest.mark.asyncio
async def test_start_game(controller, repository):
    """新しいゲームを開始する"""
    # Act: ゲームを開始
    response = await controller.start_game()

    # Assert: レスポンスの型を確認
    assert isinstance(response, StartGameResponse)
    assert response.game_id is not None
    assert isinstance(UUID(response.game_id), UUID)
    assert response.current_player == "BLACK"
    assert response.status == "playing"
    assert len(response.board_state) == 64

    # リポジトリに保存されていることを確認
    game = await repository.find_by_id(UUID(response.game_id))
    assert game is not None
    assert game.current_player == Disc.BLACK


@pytest.mark.asyncio
async def test_start_game_board_state_format(controller):
    """ゲーム開始時のboard_stateの形式が正しい"""
    # Act: ゲームを開始
    response = await controller.start_game()

    # Assert: board_stateの形式を確認
    assert all(isinstance(cell, CellState) for cell in response.board_state)

    # 初期配置を確認
    board_dict = {(cell.row, cell.col): cell.disc for cell in response.board_state}
    assert board_dict[(3, 3)] == "WHITE"
    assert board_dict[(3, 4)] == "BLACK"
    assert board_dict[(4, 3)] == "BLACK"
    assert board_dict[(4, 4)] == "WHITE"


@pytest.mark.asyncio
async def test_place_disc_success(controller, repository):
    """石を配置する"""
    # Arrange: ゲームを開始
    start_response = await controller.start_game()
    game_id = start_response.game_id

    # Act: 黒が石を置く
    response = await controller.place_disc(game_id, 2, 3)

    # Assert: レスポンスの型を確認
    assert isinstance(response, GameStateResponse)
    assert response.current_player == "WHITE"  # ターンが切り替わっている
    assert response.black_score == 4
    assert response.white_score == 1
    assert response.status == "playing"

    # board_stateに石が反映されている
    board_dict = {(cell.row, cell.col): cell.disc for cell in response.board_state}
    assert board_dict[(2, 3)] == "BLACK"
    assert board_dict[(3, 3)] == "BLACK"  # 裏返った


@pytest.mark.asyncio
async def test_place_disc_includes_valid_moves(controller):
    """石を配置後、有効手が含まれている"""
    # Arrange: ゲームを開始
    start_response = await controller.start_game()
    game_id = start_response.game_id

    # Act: 石を置く
    response = await controller.place_disc(game_id, 2, 3)

    # Assert: 有効手が含まれている
    assert isinstance(response.valid_moves, list)
    assert all(isinstance(move, Position) for move in response.valid_moves)
    assert len(response.valid_moves) > 0  # 白のターンなので有効手がある


@pytest.mark.asyncio
async def test_place_disc_game_not_found(controller):
    """存在しないゲームIDで石を置こうとするとエラー"""
    # Arrange: 存在しないゲームID
    invalid_game_id = "00000000-0000-0000-0000-000000000000"

    # Act & Assert: ValueErrorが発生
    with pytest.raises(ValueError) as exc_info:
        await controller.place_disc(invalid_game_id, 2, 3)

    assert "ゲームが見つかりません" in str(exc_info.value)


@pytest.mark.asyncio
async def test_place_disc_invalid_position(controller):
    """無効な位置に石を置こうとするとエラー"""
    # Arrange: ゲームを開始
    start_response = await controller.start_game()
    game_id = start_response.game_id

    # Act & Assert: 無効な位置(0, 0)に置こうとするとエラー
    with pytest.raises(ValueError):
        await controller.place_disc(game_id, 0, 0)


@pytest.mark.asyncio
async def test_pass_turn_success(controller, repository):
    """パスを実行する"""
    # Arrange: パスが必要な盤面を作成
    game = Game.create()

    # 黒の有効手がないように盤面を調整（白が全面を埋める）
    from src.domain.model import Board
    cells = {}
    for row in range(8):
        for col in range(8):
            cells[DomainPosition(row, col)] = Disc.WHITE

    # 1マスだけ空ける
    cells[DomainPosition(7, 7)] = Disc.EMPTY

    board = Board.reconstruct(cells)
    game = Game.reconstruct(game.id, board, Disc.BLACK, game.status)
    await repository.save(game)

    # Act: パスを実行
    response = await controller.pass_turn(str(game.id))

    # Assert: レスポンスの型を確認
    assert isinstance(response, GameStateResponse)
    # 両プレイヤーとも手がないのでゲームが終了している
    assert response.status == "finished"


@pytest.mark.asyncio
async def test_pass_turn_includes_valid_moves(controller, repository):
    """パス後、有効手が含まれている"""
    # Arrange: パスが必要な盤面
    game = Game.create()
    cells = {}
    for row in range(8):
        for col in range(8):
            cells[DomainPosition(row, col)] = Disc.WHITE
    cells[DomainPosition(7, 7)] = Disc.EMPTY

    board = Board.reconstruct(cells)
    game = Game.reconstruct(game.id, board, Disc.BLACK, game.status)
    await repository.save(game)

    # Act: パスを実行
    response = await controller.pass_turn(str(game.id))

    # Assert: valid_movesが含まれている（空の場合もある）
    assert isinstance(response.valid_moves, list)
    assert all(isinstance(move, Position) for move in response.valid_moves)


@pytest.mark.asyncio
async def test_pass_turn_game_not_found(controller):
    """存在しないゲームIDでパスしようとするとエラー"""
    # Arrange: 存在しないゲームID
    invalid_game_id = "00000000-0000-0000-0000-000000000000"

    # Act & Assert: ValueErrorが発生
    with pytest.raises(ValueError) as exc_info:
        await controller.pass_turn(invalid_game_id)

    assert "ゲームが見つかりません" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pass_turn_with_valid_moves_raises_error(controller):
    """有効な手がある場合はパスできない"""
    # Arrange: 通常のゲーム（有効手がある）
    start_response = await controller.start_game()
    game_id = start_response.game_id

    # Act & Assert: 有効手があるのでパスできない
    with pytest.raises(ValueError) as exc_info:
        await controller.pass_turn(game_id)

    assert "パスできません" in str(exc_info.value)


@pytest.mark.asyncio
async def test_multiple_games_isolated(controller):
    """複数のゲームが独立して管理される"""
    # Arrange & Act: 2つのゲームを開始
    response1 = await controller.start_game()
    response2 = await controller.start_game()

    # Assert: 異なるゲームIDを持つ
    assert response1.game_id != response2.game_id

    # 一方のゲームで石を置く
    await controller.place_disc(response1.game_id, 2, 3)

    # もう一方のゲームは影響を受けない
    response2_state = await controller.place_disc(response2.game_id, 2, 3)
    assert response2_state.current_player == "WHITE"


@pytest.mark.asyncio
async def test_game_state_response_completeness(controller):
    """GameStateResponseがすべての必要な情報を含む"""
    # Arrange: ゲームを開始して石を置く
    start_response = await controller.start_game()
    game_id = start_response.game_id

    # Act: 石を置く
    response = await controller.place_disc(game_id, 2, 3)

    # Assert: すべてのフィールドが存在する
    assert hasattr(response, "board_state")
    assert hasattr(response, "current_player")
    assert hasattr(response, "black_score")
    assert hasattr(response, "white_score")
    assert hasattr(response, "status")
    assert hasattr(response, "valid_moves")

    # 値が正しい型である
    assert isinstance(response.board_state, list)
    assert isinstance(response.current_player, str)
    assert isinstance(response.black_score, int)
    assert isinstance(response.white_score, int)
    assert isinstance(response.status, str)
    assert isinstance(response.valid_moves, list)

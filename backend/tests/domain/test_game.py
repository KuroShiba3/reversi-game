import pytest
from uuid import uuid4
from domain.model.game import Game
from domain.model.board import Board
from domain.model.disc import Disc
from domain.model.position import Position
from domain.model.game_status import GameStatus


def test_game_create():
    """ゲーム作成テスト - 初期状態を確認"""
    game = Game.create()

    assert game.id is not None
    assert game.current_player == Disc.BLACK
    assert game.status == GameStatus.PLAYING
    assert game.result is None

    # 初期配置の確認
    assert game.board.cells[Position(3, 3)] == Disc.WHITE
    assert game.board.cells[Position(3, 4)] == Disc.BLACK
    assert game.board.cells[Position(4, 3)] == Disc.BLACK
    assert game.board.cells[Position(4, 4)] == Disc.WHITE


def test_game_reconstruct():
    """ゲーム再構築テスト"""
    game_id = uuid4()
    board = Board.create()

    game = Game.reconstruct(
        id=game_id,
        board=board,
        current_player=Disc.WHITE,
        status=GameStatus.PLAYING
    )

    assert game.id == game_id
    assert game.current_player == Disc.WHITE
    assert game.status == GameStatus.PLAYING
    assert game.result is None


def test_game_place_disc():
    """石を置くテスト - ターンが切り替わることを確認"""
    game = Game.create()

    # 黒のターン
    assert game.current_player == Disc.BLACK

    # 黒が石を置く
    game.place_disc(Position(2, 3), Disc.BLACK)

    # ターンが白に切り替わる
    assert game.current_player == Disc.WHITE

    # 盤面が更新されている
    assert game.board.cells[Position(2, 3)] == Disc.BLACK
    assert game.board.cells[Position(3, 3)] == Disc.BLACK


def test_game_place_disc_white():
    """白が石を置くテスト"""
    game = Game.create()

    # 黒のターンをスキップして白のターンにする
    game.place_disc(Position(2, 3), Disc.BLACK)

    # 白のターン
    assert game.current_player == Disc.WHITE

    # 白が石を置く
    game.place_disc(Position(2, 2), Disc.WHITE)

    # ターンが黒に戻る
    assert game.current_player == Disc.BLACK


def test_game_get_valid_moves_initial():
    """初期状態の有効手取得テスト"""
    game = Game.create()

    # 現在のプレイヤー（黒）の有効手
    valid_moves = game.get_valid_moves()
    assert len(valid_moves) == 4
    assert Position(2, 3) in valid_moves
    assert Position(3, 2) in valid_moves
    assert Position(4, 5) in valid_moves
    assert Position(5, 4) in valid_moves

    # 白の有効手を明示的に取得
    white_moves = game.get_valid_moves(Disc.WHITE)
    assert len(white_moves) == 4


def test_game_get_valid_moves_finished():
    """終了したゲームでは有効手が空リストになることを確認"""
    game = Game.create()
    game._status = GameStatus.FINISHED

    valid_moves = game.get_valid_moves()
    assert valid_moves == []


def test_game_pass_turn():
    """パスターンのテスト"""
    game = Game.create()

    # 黒のターン
    assert game.current_player == Disc.BLACK

    # パス
    game.pass_turn()

    # 白のターンに切り替わる
    assert game.current_player == Disc.WHITE

    # もう一度パス
    game.pass_turn()

    # 黒のターンに戻る
    assert game.current_player == Disc.BLACK


def test_game_can_current_player_move():
    """現在のプレイヤーが手を打てるかのテスト"""
    game = Game.create()

    # 初期状態では黒は手を打てる
    assert game.can_current_player_move() is True


def test_game_get_scores_initial():
    """初期状態のスコア取得テスト"""
    game = Game.create()

    black_score, white_score = game.get_scores()
    assert black_score == 2
    assert white_score == 2


def test_game_get_scores_after_move():
    """石を置いた後のスコア取得テスト"""
    game = Game.create()

    # 黒が石を置く
    game.place_disc(Position(2, 3), Disc.BLACK)

    black_score, white_score = game.get_scores()
    assert black_score == 4  # 2 + 置いた石1 + 裏返した石1
    assert white_score == 1  # 2 - 裏返された石1


def test_game_is_game_over_initial():
    """初期状態ではゲームが終了していないことを確認"""
    game = Game.create()

    assert game.is_game_over() is False


def test_game_is_game_over_when_finished():
    """ステータスがFINISHEDの時はゲーム終了"""
    game = Game.create()
    game._status = GameStatus.FINISHED

    assert game.is_game_over() is True


def test_game_is_game_over_no_valid_moves():
    """両プレイヤーが手を打てない時はゲーム終了"""
    # 両プレイヤーが手を打てない盤面を作成
    cells = {}
    for row in range(8):
        for col in range(8):
            cells[Position(row, col)] = Disc.BLACK

    board = Board.reconstruct(cells)
    game = Game.reconstruct(uuid4(), board, Disc.BLACK, GameStatus.PLAYING)

    # 黒も白も手を打てない
    assert game.is_game_over() is True


def test_game_finish(mocker):
    """ゲーム終了テスト"""
    game = Game.create()

    # datetime.nowをモック
    from datetime import datetime
    fixed_time = datetime(2025, 12, 22, 15, 0, 0)
    mock_datetime = mocker.patch('domain.model.game_result.datetime')
    mock_datetime.now.return_value = fixed_time

    # ゲームを終了
    game.finish()

    # ステータスが終了になっている
    assert game.status == GameStatus.FINISHED

    # GameResultが作成されている
    assert game.result is not None
    assert game.result.game_id == game.id
    assert game.result.black_score == 2
    assert game.result.white_score == 2
    assert game.result.winner is None  # 引き分け
    assert game.result.finished_at == fixed_time


def test_game_finish_black_wins(mocker):
    """黒が勝った状態でゲーム終了"""
    game = Game.create()

    # 黒が優勢な盤面を作る
    game.place_disc(Position(2, 3), Disc.BLACK)

    from datetime import datetime
    fixed_time = datetime(2025, 12, 22, 16, 0, 0)
    mock_datetime = mocker.patch('domain.model.game_result.datetime')
    mock_datetime.now.return_value = fixed_time

    game.finish()

    assert game.result is not None
    assert game.result.winner == Disc.BLACK
    assert game.result.black_score > game.result.white_score


def test_game_finish_already_finished():
    """すでに終了したゲームを再度終了しようとするとエラー"""
    game = Game.create()
    game._status = GameStatus.FINISHED

    with pytest.raises(ValueError) as exc_info:
        game.finish()

    assert str(exc_info.value) == "ゲームはすでに終了しています。"


def test_game_full_gameplay():
    """実際のゲームプレイのシミュレーション"""
    game = Game.create()

    # 黒のターン
    assert game.current_player == Disc.BLACK
    valid_moves = game.get_valid_moves()
    assert len(valid_moves) > 0

    # 黒が手を打つ
    game.place_disc(valid_moves[0], Disc.BLACK)

    # 白のターン
    assert game.current_player == Disc.WHITE
    white_moves = game.get_valid_moves()
    assert len(white_moves) > 0

    # 白が手を打つ
    game.place_disc(white_moves[0], Disc.WHITE)

    # 黒のターンに戻る
    assert game.current_player == Disc.BLACK

    # ゲームはまだ終了していない
    assert game.is_game_over() is False
    assert game.status == GameStatus.PLAYING

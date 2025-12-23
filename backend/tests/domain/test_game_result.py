import pytest
from datetime import datetime
from uuid import uuid4
from domain.model.game_result import GameResult
from domain.model.disc import Disc


def test_game_result_create_black_wins(mocker):
    """黒が勝つ場合のGameResult作成テスト"""
    game_id = uuid4()
    fixed_time = datetime(2025, 12, 22, 10, 30, 0)

    # datetime.nowを固定の時刻にモック
    mock_datetime = mocker.patch('domain.model.game_result.datetime')
    mock_datetime.now.return_value = fixed_time

    result = GameResult.create(game_id, black_score=35, white_score=29)

    assert result.game_id == game_id
    assert result.winner == Disc.BLACK
    assert result.black_score == 35
    assert result.white_score == 29
    assert result.finished_at == fixed_time


def test_game_result_create_white_wins(mocker):
    """白が勝つ場合のGameResult作成テスト"""
    game_id = uuid4()
    fixed_time = datetime(2025, 12, 22, 11, 0, 0)

    mock_datetime = mocker.patch('domain.model.game_result.datetime')
    mock_datetime.now.return_value = fixed_time

    result = GameResult.create(game_id, black_score=28, white_score=36)

    assert result.game_id == game_id
    assert result.winner == Disc.WHITE
    assert result.black_score == 28
    assert result.white_score == 36
    assert result.finished_at == fixed_time


def test_game_result_create_draw(mocker):
    """引き分けの場合のGameResult作成テスト"""
    game_id = uuid4()
    fixed_time = datetime(2025, 12, 22, 12, 0, 0)

    mock_datetime = mocker.patch('domain.model.game_result.datetime')
    mock_datetime.now.return_value = fixed_time

    result = GameResult.create(game_id, black_score=32, white_score=32)

    assert result.game_id == game_id
    assert result.winner is None  # 引き分け
    assert result.black_score == 32
    assert result.white_score == 32
    assert result.finished_at == fixed_time


@pytest.mark.parametrize("black_score,white_score,error_message,description", [
    (-1, 30, "黒のスコアは0から64の範囲内である必要があります。", "黒スコアが負の値"),
    (65, 30, "黒のスコアは0から64の範囲内である必要があります。", "黒スコアが64超過"),
    (30, -1, "白のスコアは0から64の範囲内である必要があります。", "白スコアが負の値"),
    (30, 65, "白のスコアは0から64の範囲内である必要があります。", "白スコアが64超過"),
])
def test_game_result_invalid_scores(black_score, white_score, error_message, description):
    """無効なスコアでGameResultを作成しようとした場合のテスト"""
    game_id = uuid4()

    with pytest.raises(ValueError) as exc_info:
        GameResult(game_id, None, black_score, white_score, datetime.now())

    assert str(exc_info.value) == error_message, f"{description}: エラーメッセージが一致しません"


def test_game_result_reconstruct():
    """reconstructメソッドのテスト"""
    game_id = uuid4()
    finished_at = datetime(2025, 12, 22, 13, 0, 0)

    result = GameResult.reconstruct(
        game_id=game_id,
        winner=Disc.BLACK,
        black_score=40,
        white_score=24,
        finished_at=finished_at
    )

    assert result.game_id == game_id
    assert result.winner == Disc.BLACK
    assert result.black_score == 40
    assert result.white_score == 24
    assert result.finished_at == finished_at


@pytest.mark.parametrize("winner,expected_db_value,description", [
    (Disc.BLACK, 1, "黒勝ち"),
    (Disc.WHITE, 2, "白勝ち"),
    (None, 3, "引き分け"),
])
def test_to_db_winner_value(winner, expected_db_value, description):
    """to_db_winner_valueのテスト"""
    game_id = uuid4()
    finished_at = datetime.now()

    result = GameResult(game_id, winner, 30, 34, finished_at)

    assert result.to_db_winner_value() == expected_db_value, f"{description}: DB値が一致しません"

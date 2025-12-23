import pytest
from domain.model.position import Position


def test_position_create_valid():
    """有効な位置の作成テスト"""
    pos = Position(3, 4)
    assert pos.row == 3
    assert pos.col == 4


def test_position_create_boundaries():
    """境界値のテスト - 有効な範囲（0-7）"""
    # 左上の角
    pos1 = Position(0, 0)
    assert pos1.row == 0
    assert pos1.col == 0

    # 右下の角
    pos2 = Position(7, 7)
    assert pos2.row == 7
    assert pos2.col == 7

    # その他の境界値
    pos3 = Position(0, 7)
    assert pos3.row == 0
    assert pos3.col == 7

    pos4 = Position(7, 0)
    assert pos4.row == 7
    assert pos4.col == 0


@pytest.mark.parametrize("row,col,description", [
    (-1, 0, "行が負の値"),
    (0, -1, "列が負の値"),
    (8, 0, "行が8（範囲外）"),
    (0, 8, "列が8（範囲外）"),
    (-1, -1, "行と列が負の値"),
    (8, 8, "行と列が8（範囲外）"),
    (10, 5, "行が大きすぎる"),
    (5, 10, "列が大きすぎる"),
])
def test_position_create_invalid(row, col, description):
    """無効な位置の作成テスト"""
    with pytest.raises(ValueError) as exc_info:
        Position(row, col)

    assert str(exc_info.value) == "行と列は0から7の範囲内である必要があります。", \
        f"{description}: エラーメッセージが一致しません"


def test_position_equality():
    """等価性テスト - 同じ座標は等しい"""
    pos1 = Position(3, 4)
    pos2 = Position(3, 4)
    pos3 = Position(3, 5)

    assert pos1 == pos2, "同じ座標の Position は等しいべき"
    assert pos1 != pos3, "異なる座標の Position は等しくないべき"
    assert pos2 != pos3, "異なる座標の Position は等しくないべき"


def test_position_equality_with_non_position():
    """等価性テスト - Position以外のオブジェクトとの比較"""
    pos = Position(3, 4)

    assert pos != (3, 4), "タプルとは等しくない"
    assert pos != "Position(3, 4)", "文字列とは等しくない"
    assert pos != None, "Noneとは等しくない"
    assert pos != 3, "数値とは等しくない"


def test_position_hash():
    """ハッシュ化テスト - 辞書のキーとして使える"""
    pos1 = Position(3, 4)
    pos2 = Position(3, 4)
    pos3 = Position(5, 6)

    # 同じ座標は同じハッシュ値
    assert hash(pos1) == hash(pos2)

    # 異なる座標は異なるハッシュ値（通常）
    assert hash(pos1) != hash(pos3)


def test_position_as_dict_key():
    """辞書のキーとして使えることを確認"""
    board = {}
    pos1 = Position(3, 4)
    pos2 = Position(3, 4)
    pos3 = Position(5, 6)

    board[pos1] = "黒"
    board[pos3] = "白"

    # 同じ座標で値を取得できる
    assert board[pos2] == "黒"
    assert board[pos3] == "白"

    # 辞書のキーとして正しく動作
    assert len(board) == 2


def test_position_in_set():
    """セットのメンバーとして使えることを確認"""
    positions = set()
    pos1 = Position(3, 4)
    pos2 = Position(3, 4)
    pos3 = Position(5, 6)

    positions.add(pos1)
    positions.add(pos2)  # 同じ座標なので追加されない
    positions.add(pos3)

    assert len(positions) == 2
    assert pos1 in positions
    assert pos2 in positions
    assert pos3 in positions


@pytest.mark.parametrize("row,col", [
    (0, 0), (0, 7), (7, 0), (7, 7),  # 4つの角
    (0, 3), (3, 0), (7, 3), (3, 7),  # 4辺の中央
    (3, 3), (3, 4), (4, 3), (4, 4),  # 中央付近
])
def test_position_all_valid_coordinates(row, col):
    """全ての有効な座標でPositionが作成できることを確認"""
    pos = Position(row, col)
    assert pos.row == row
    assert pos.col == col

import pytest
from domain.model.board import Board
from domain.model.disc import Disc
from domain.model.position import Position

def test_board_create():
    board = Board.create()
    for row in range(8):
        for col in range(8):
            pos = Position(row, col)
            if (row, col) in [(3, 3), (4, 4)]:
                assert board.cells[pos] == Disc.WHITE
            elif (row, col) in [(3, 4), (4, 3)]:
                assert board.cells[pos] == Disc.BLACK
            else:
                assert board.cells[pos] == Disc.EMPTY

def test_board_place_disc_and_flip():
    board = Board.create()
    position = Position(2, 3)
    board.place_disc(position, Disc.BLACK)

    assert board.cells[position] == Disc.BLACK
    assert board.cells[Position(3, 3)] == Disc.BLACK

    position = Position(2, 2)
    board.place_disc(position, Disc.WHITE)

    assert board.cells[position] == Disc.WHITE
    assert board.cells[Position(3, 3)] == Disc.WHITE

@pytest.mark.parametrize("initial_setup,place_pos,disc,expected_flips,description", [
    # 上方向 (UP)
    (
        {Position(3, 3): Disc.WHITE, Position(2, 3): Disc.WHITE, Position(1, 3): Disc.WHITE},
        Position(0, 3),
        Disc.BLACK,
        [Position(0, 3), Position(1, 3), Position(2, 3), Position(3, 3)],
        "上方向"
    ),
    # 下方向 (DOWN)
    (
        {Position(3, 3): Disc.WHITE, Position(4, 3): Disc.WHITE, Position(5, 3): Disc.WHITE},
        Position(6, 3),
        Disc.BLACK,
        [Position(6, 3), Position(5, 3), Position(4, 3), Position(3, 3)],
        "下方向"
    ),
    # 左方向 (LEFT)
    (
        {Position(3, 3): Disc.WHITE, Position(3, 2): Disc.WHITE, Position(3, 1): Disc.WHITE},
        Position(3, 0),
        Disc.BLACK,
        [Position(3, 0), Position(3, 1), Position(3, 2), Position(3, 3)],
        "左方向"
    ),
    # 右方向 (RIGHT)
    (
        {Position(3, 3): Disc.WHITE, Position(3, 4): Disc.WHITE, Position(3, 5): Disc.WHITE},
        Position(3, 6),
        Disc.BLACK,
        [Position(3, 6), Position(3, 5), Position(3, 4), Position(3, 3)],
        "右方向"
    ),
    # 左上方向 (UP-LEFT)
    (
        {Position(3, 3): Disc.WHITE, Position(2, 2): Disc.WHITE, Position(1, 1): Disc.WHITE},
        Position(0, 0),
        Disc.BLACK,
        [Position(0, 0), Position(1, 1), Position(2, 2), Position(3, 3)],
        "左上方向"
    ),
    # 右上方向 (UP-RIGHT)
    (
        {Position(3, 3): Disc.WHITE, Position(2, 4): Disc.WHITE, Position(1, 5): Disc.WHITE},
        Position(0, 6),
        Disc.BLACK,
        [Position(0, 6), Position(1, 5), Position(2, 4), Position(3, 3)],
        "右上方向"
    ),
    # 左下方向 (DOWN-LEFT)
    (
        {Position(3, 3): Disc.WHITE, Position(4, 2): Disc.WHITE, Position(5, 1): Disc.WHITE},
        Position(6, 0),
        Disc.BLACK,
        [Position(6, 0), Position(5, 1), Position(4, 2), Position(3, 3)],
        "左下方向"
    ),
    # 右下方向 (DOWN-RIGHT)
    (
        {Position(3, 3): Disc.WHITE, Position(4, 4): Disc.WHITE, Position(5, 5): Disc.WHITE},
        Position(6, 6),
        Disc.BLACK,
        [Position(6, 6), Position(5, 5), Position(4, 4), Position(3, 3)],
        "右下方向"
    ),
])
def test_board_place_disc_flip_all_directions(initial_setup, place_pos, disc, expected_flips, description):
    """8方向すべての裏返しをテスト"""
    # 空のボードを作成
    cells = {}
    for row in range(8):
        for col in range(8):
            cells[Position(row, col)] = Disc.EMPTY

    # 初期配置を設定（WHITE の石を配置し、最後に BLACK を置く）
    for pos, disc_color in initial_setup.items():
        cells[pos] = disc_color

    # BLACKの石を端に置いて挟む
    cells[expected_flips[-1]] = Disc.BLACK

    board = Board.reconstruct(cells)

    # 石を置く
    board.place_disc(place_pos, disc)

    # すべての位置が指定した色になっていることを確認
    for pos in expected_flips:
        assert board.cells[pos] == disc, f"{description}: 位置{pos}は{disc}であるべきです"

@pytest.mark.parametrize("board_setup,disc,expected_positions,description", [
    # ゲーム開始直後の黒の有効手
    (
        "initial",
        Disc.BLACK,
        [Position(2, 3), Position(3, 2), Position(4, 5), Position(5, 4)],
        "初期配置-黒の有効手"
    ),
    # ゲーム開始直後の白の有効手
    (
        "initial",
        Disc.WHITE,
        [Position(2, 4), Position(3, 5), Position(4, 2), Position(5, 3)],
        "初期配置-白の有効手"
    ),
    # 有効手が1つだけ
    (
        {
            Position(3, 3): Disc.BLACK,
            Position(3, 4): Disc.WHITE,
            Position(3, 5): Disc.WHITE,
        },
        Disc.BLACK,
        [Position(3, 6)],
        "有効手が1つだけ"
    ),
    # 角に置ける場合
    (
        {
            Position(0, 1): Disc.WHITE,
            Position(0, 2): Disc.BLACK,
        },
        Disc.BLACK,
        [Position(0, 0)],
        "角に置ける"
    ),
    # 有効手なし（パスが必要）
    (
        {
            Position(0, 0): Disc.BLACK,
            Position(0, 1): Disc.BLACK,
            Position(1, 0): Disc.BLACK,
        },
        Disc.WHITE,
        [],
        "有効手なし-パス"
    ),
])
def test_get_valid_moves(board_setup, disc, expected_positions, description):
    """get_valid_movesのテスト - 様々な盤面パターン"""
    # ボードの準備
    if board_setup == "initial":
        board = Board.create()
    else:
        # カスタム盤面を作成
        cells = {}
        for row in range(8):
            for col in range(8):
                cells[Position(row, col)] = Disc.EMPTY

        for pos, disc_color in board_setup.items():
            cells[pos] = disc_color

        # 相手の石も配置（挟むため）
        opponent = Disc.WHITE if disc == Disc.BLACK else Disc.BLACK
        # 各expected_positionに対して、挟むための石を配置
        for expected_pos in expected_positions:
            # 8方向をチェックして、挟める位置に相手の石を配置
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                         (0, 1), (1, -1), (1, 0), (1, 1)]
            for dr, dc in directions:
                r, c = expected_pos.row + dr, expected_pos.col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    pos = Position(r, c)
                    if pos in board_setup and board_setup[pos] == opponent:
                        # すでに相手の石がある場合、その先に自分の石が必要
                        # この簡易実装では board_setup に含まれていると仮定
                        pass

        board = Board.reconstruct(cells)

    # 有効手を取得
    valid_moves = board.get_valid_moves(disc)

    # ソートして比較（順序は問わない）
    assert sorted(valid_moves, key=lambda p: (p.row, p.col)) == \
           sorted(expected_positions, key=lambda p: (p.row, p.col)), \
           f"{description}: 期待される有効手と一致しません"

@pytest.mark.parametrize("board_setup,place_pos,disc,error_message,description", [
    # すでに石がある位置に置こうとする
    (
        "initial",
        Position(3, 3),  # 初期配置で白石がある位置
        Disc.BLACK,
        "指定された位置に石を置くことはできません",
        "すでに石がある位置"
    ),
    # 挟めない位置に置こうとする（空きマスだが無効）
    (
        "initial",
        Position(0, 0),  # 角は初期配置では置けない
        Disc.BLACK,
        "指定された位置に石を置くことはできません",
        "挟めない位置"
    ),
    # 相手の石がない方向
    (
        {
            Position(3, 3): Disc.BLACK,
        },
        Position(3, 5),  # 間に相手の石がない
        Disc.BLACK,
        "指定された位置に石を置くことはできません",
        "相手の石がない"
    ),
])
def test_place_disc_invalid_position(board_setup, place_pos, disc, error_message, description):
    """place_discで無効な位置に置こうとした場合のテスト"""
    # ボードの準備
    if board_setup == "initial":
        board = Board.create()
    else:
        cells = {}
        for row in range(8):
            for col in range(8):
                cells[Position(row, col)] = Disc.EMPTY

        for pos, disc_color in board_setup.items():
            cells[pos] = disc_color

        board = Board.reconstruct(cells)

    # ValueErrorが発生することを確認
    with pytest.raises(ValueError) as exc_info:
        board.place_disc(place_pos, disc)

    # エラーメッセージが正しいことを確認
    assert str(exc_info.value) == error_message, f"{description}: エラーメッセージが一致しません"

def test_board_reconstruct():
    """reconstructメソッドのテスト - DBから復元した盤面を再構築"""
    # カスタム盤面を作成
    cells = {}
    for row in range(8):
        for col in range(8):
            cells[Position(row, col)] = Disc.EMPTY

    # 特定の盤面配置を設定
    cells[Position(0, 0)] = Disc.BLACK
    cells[Position(0, 1)] = Disc.WHITE
    cells[Position(3, 3)] = Disc.WHITE
    cells[Position(3, 4)] = Disc.BLACK
    cells[Position(4, 3)] = Disc.BLACK
    cells[Position(4, 4)] = Disc.WHITE
    cells[Position(7, 7)] = Disc.BLACK

    # reconstructで復元
    board = Board.reconstruct(cells)

    # 復元された盤面が正しいことを確認
    assert board.cells[Position(0, 0)] == Disc.BLACK
    assert board.cells[Position(0, 1)] == Disc.WHITE
    assert board.cells[Position(3, 3)] == Disc.WHITE
    assert board.cells[Position(3, 4)] == Disc.BLACK
    assert board.cells[Position(4, 3)] == Disc.BLACK
    assert board.cells[Position(4, 4)] == Disc.WHITE
    assert board.cells[Position(7, 7)] == Disc.BLACK
    assert board.cells[Position(1, 1)] == Disc.EMPTY

def test_board_reconstruct_full_board():
    """reconstructメソッドのテスト - 盤面が埋まっている状態を復元"""
    cells = {}

    # 盤面を黒と白で交互に埋める
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                cells[Position(row, col)] = Disc.BLACK
            else:
                cells[Position(row, col)] = Disc.WHITE

    board = Board.reconstruct(cells)

    # 復元された盤面が正しいことを確認
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                assert board.cells[Position(row, col)] == Disc.BLACK
            else:
                assert board.cells[Position(row, col)] == Disc.WHITE
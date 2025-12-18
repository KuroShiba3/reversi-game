from uuid import UUID
from psycopg_pool import AsyncConnectionPool

from src.domain.repository.game_repository import IGameRepository
from src.domain.model import Game, Board, Disc, Position, GameStatus


class GameRepositoryImpl(IGameRepository):
    """ゲームリポジトリのPostgreSQL実装"""

    def __init__(self, pool: AsyncConnectionPool):
        self._pool = pool

    async def save(self, game: Game) -> None:
        """
        ゲームを保存（新規作成または更新）
        ゲームが終了している場合（game.result が存在する場合）は結果も1トランザクションで保存
        """
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                # 1. gamesテーブルに保存（UPSERT）
                await cur.execute(
                    """
                    INSERT INTO games (id, current_player, status, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                    ON CONFLICT (id) DO UPDATE SET
                        current_player = EXCLUDED.current_player,
                        status = EXCLUDED.status,
                        updated_at = NOW()
                    """,
                    (str(game.id), game.current_player.value, game.status.value),
                )

                # 2. board_cellsを一括UPSERT
                cell_data = [
                    (str(game.id), pos.row, pos.col, disc.value)
                    for pos, disc in game.board.cells.items()
                ]

                await cur.executemany(
                    """
                    INSERT INTO board_cells (game_id, row, col, disc, updated_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (game_id, row, col) DO UPDATE SET
                        disc = EXCLUDED.disc,
                        updated_at = NOW()
                    """,
                    cell_data,
                )

                # 3. ゲーム結果を保存（game.resultが存在する場合のみ）
                if game.result is not None:
                    await cur.execute(
                        """
                        INSERT INTO game_results (game_id, winner, black_score, white_score, finished_at)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            str(game.result.game_id),
                            game.result.to_db_winner_value(),
                            game.result.black_score,
                            game.result.white_score,
                            game.result.finished_at,
                        ),
                    )

    async def find_by_id(self, game_id: UUID) -> Game | None:
        """IDでゲームを検索"""
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                # gamesテーブルから取得
                await cur.execute(
                    "SELECT id, current_player, status FROM games WHERE id = %s",
                    (str(game_id),),
                )
                game_row = await cur.fetchone()

                if not game_row:
                    return None

                # board_cellsを取得
                await cur.execute(
                    "SELECT row, col, disc FROM board_cells WHERE game_id = %s ORDER BY row, col",
                    (str(game_id),),
                )
                cell_rows = await cur.fetchall()

                # Boardを復元
                cells = {}
                for cell in cell_rows:
                    pos = Position(cell["row"], cell["col"])
                    disc = Disc(cell["disc"])
                    cells[pos] = disc

                board = Board.reconstruct(cells)
                current_player = Disc(game_row["current_player"])
                status = GameStatus(game_row["status"])

                return Game.reconstruct(game_id, board, current_player, status)

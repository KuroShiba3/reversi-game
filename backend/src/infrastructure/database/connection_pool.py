from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

from ...config import POSTGRES_URL


class DatabasePool:
    """データベース接続プール管理クラス"""

    _pool: AsyncConnectionPool | None = None

    @classmethod
    async def initialize(cls, min_size: int = 2, max_size: int = 10):
        """
        接続プールを初期化（アプリ起動時に1度だけ呼ぶ）

        Args:
            min_size: 最小接続数
            max_size: 最大接続数
        """
        if cls._pool is None:
            cls._pool = AsyncConnectionPool(
                POSTGRES_URL,
                kwargs={"row_factory": dict_row},
                min_size=min_size,
                max_size=max_size,
            )
            await cls._pool.open()

    @classmethod
    async def close(cls):
        """接続プールをクローズ"""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None

    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        """データベース接続を取得"""
        if cls._pool is None:
            raise RuntimeError("DatabasePoolが初期化されていません。initialize()を呼んでください。")

        async with cls._pool.connection() as conn:
            yield conn

    @classmethod
    def get_pool(cls) -> AsyncConnectionPool:
        """接続プールを取得"""
        if cls._pool is None:
            raise RuntimeError("DatabasePoolが初期化されていません。initialize()を呼んでください。")
        return cls._pool

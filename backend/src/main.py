from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from .infrastructure.database.connection_pool import DatabasePool
from .infrastructure.database.migration import run_migrations
from .presentation.game_router import router as game_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    print("アプリ起動中...")

    # マイグレーション実行
    run_migrations()
    print("マイグレーション成功しました。")

    # データベース接続プール初期化
    await DatabasePool.initialize(min_size=2, max_size=10)
    print("データベース接続プール初期化完了")

    yield

    # クリーンアップ
    await DatabasePool.close()
    print("データベース接続プールをクローズしました。")


app = FastAPI(lifespan=lifespan)

app.include_router(game_router)


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

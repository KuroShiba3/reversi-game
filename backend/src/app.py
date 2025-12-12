from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from .db.migrate import run_migrations
from .models import User
from sqlalchemy.orm import sessionmaker
from .db.setting import engine

SessionClass = sessionmaker(engine)
session = SessionClass()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("アプリ起動中...")
    run_migrations()
    print("マイグレーション成功しました。")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    user = User(name="John2", fullname="John Doe", nickname="johnny")
    session.add(user)
    session.commit()
    return {"message": "success"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
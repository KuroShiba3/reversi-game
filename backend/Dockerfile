# ビルドステージ
FROM ghcr.io/astral-sh/uv:0.9.2-python3.12-bookworm-slim AS builder
WORKDIR /app
ENV UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# 開発環境用
FROM builder AS development
ENV PYTHONUNBUFFERED=1
CMD ["uv", "run", "--no-sync", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 本番ステージ
FROM python:3.12-slim-bookworm AS production
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY --from=builder /app/.venv /app/.venv
COPY ./src ./src
COPY ./migrations ./migrations
COPY ./alembic.ini ./alembic.ini
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
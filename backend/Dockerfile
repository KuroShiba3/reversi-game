FROM ghcr.io/astral-sh/uv:0.9.2-python3.13-bookworm-slim AS builder
WORKDIR /app
ENV UV_LINK_MODE=copy
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen || uv sync

# 開発環境用
FROM builder AS development
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"
COPY ./src ./src
COPY ./migrations ./migrations
CMD ["uv", "run", "--no-sync", "python", "-m", "src.main"]

# 本番ステージ
FROM python:3.13-slim-bookworm AS production
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=builder /app/.venv /app/.venv
COPY ./src ./src
COPY ./migrations ./migrations
CMD ["python", "-m", "src.main"]

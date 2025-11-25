FROM python:3.12-slim AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"

COPY backend/app/pyproject.toml /app/pyproject.toml
COPY backend/app/shared/pyproject.toml /app/shared/pyproject.toml
COPY backend/app/services/ai_service/pyproject.toml /app/services/ai_service/pyproject.toml
COPY backend/app/shared /app/shared
COPY backend/app/services/ai_service/ai_service /app/services/ai_service/ai_service

RUN uv sync --package ai_service --no-dev --no-cache

RUN rm -rf /root/.cache

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/services/ai_service/ai_service /app/services/ai_service/ai_service
COPY --from=builder /app/shared /app/shared

RUN rm -rf /app/.venv/lib/python*/site-packages/nvidia \
           /app/.venv/lib/python*/site-packages/cudnn* || true

EXPOSE 8004
CMD ["uvicorn", "ai_service.main:app", "--host", "0.0.0.0", "--port", "8004"]

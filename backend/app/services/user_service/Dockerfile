# Builder stage
FROM python:3.12-slim AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
COPY backend/app/pyproject.toml /app/pyproject.toml
COPY backend/app/shared/pyproject.toml /app/shared/pyproject.toml
COPY backend/app/services/user_service/pyproject.toml /app/services/user_service/pyproject.toml
COPY backend/app/shared/shared /app/shared/shared
COPY backend/app/services/user_service/user_service /app/services/user_service/user_service
# Use cache mount for uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package user_service --no-dev

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/app/.venv/bin:$PATH" PYTHONPATH=/app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/services/user_service/user_service /app/services/user_service/user_service
COPY --from=builder /app/shared /app/shared
EXPOSE 8001
CMD ["uvicorn", "user_service.main:app", "--host", "0.0.0.0", "--port", "8001"]

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
COPY backend/app/pyproject.toml /app/pyproject.toml
COPY backend/app/shared/pyproject.toml /app/shared/pyproject.toml
COPY backend/app/services/ai_service/pyproject.toml /app/services/ai_service/pyproject.toml
COPY backend/app/shared/shared /app/shared/shared
COPY backend/app/services/ai_service/ai_service /app/services/ai_service/ai_service
RUN uv sync --package ai_service --no-dev
RUN rm -rf /app/.venv/lib/python*/site-packages/nvidia /app/.venv/lib/python*/site-packages/cudnn* || true
ENV PYTHONPATH=/app
EXPOSE 8004
CMD ["uv", "run", "--package", "ai_service", "uvicorn", "ai_service.main:app", "--host", "0.0.0.0", "--port", "8004"]
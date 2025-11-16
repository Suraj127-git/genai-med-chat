FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
COPY backend/app/pyproject.toml /app/pyproject.toml
COPY backend/app/shared/pyproject.toml /app/shared/pyproject.toml
COPY backend/app/services/chat_service/pyproject.toml /app/services/chat_service/pyproject.toml
COPY backend/app/shared/shared /app/shared/shared
COPY backend/app/services/chat_service/chat_service /app/services/chat_service/chat_service
RUN uv sync --package chat_service --no-dev
RUN rm -rf /app/.venv/lib/python*/site-packages/nvidia /app/.venv/lib/python*/site-packages/cudnn* || true
ENV PYTHONPATH=/app
EXPOSE 8003
CMD ["uv", "run", "--package", "chat_service", "uvicorn", "chat_service.main:app", "--host", "0.0.0.0", "--port", "8003"]

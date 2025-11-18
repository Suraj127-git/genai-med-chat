FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
COPY backend/app/pyproject.toml /app/pyproject.toml
COPY backend/app/shared/pyproject.toml /app/shared/pyproject.toml
COPY backend/app/gateway/pyproject.toml /app/gateway/pyproject.toml
COPY backend/app/shared/shared /app/shared/shared
COPY backend/app/gateway/gateway /app/gateway/gateway
RUN uv sync --package gateway --no-dev
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uv", "run", "--package", "gateway", "uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Builder stage
FROM python:3.12-slim AS builder
WORKDIR /app/worker
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
COPY backend/worker /app/worker
COPY backend/app/shared /app/shared
# Use cache mount for uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv && . .venv/bin/activate && uv pip install "celery[redis]" requests \
    opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp \
    opentelemetry-instrumentation-requests opentelemetry-instrumentation-logging

# Runtime stage
FROM python:3.12-slim
WORKDIR /app/worker
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/app/worker/.venv/bin:$PATH" PYTHONPATH=/app
COPY --from=builder /app/worker /app/worker
COPY --from=builder /app/shared /app/shared
CMD ["celery", "-A", "celery_worker.celery_app", "worker", "--loglevel=info"]

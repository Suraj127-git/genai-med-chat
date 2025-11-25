# Builder stage
FROM python:3.12-slim AS builder
WORKDIR /app/worker
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends python3-venv && rm -rf /var/lib/apt/lists/*
COPY backend/worker /app/worker
COPY backend/app/shared /app/shared
# Create virtualenv outside app directory so bind mounts don't overwrite it
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir "celery[redis]" requests \
    opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp \
    opentelemetry-instrumentation-requests opentelemetry-instrumentation-logging

# Runtime stage
FROM python:3.12-slim
WORKDIR /app/worker
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/worker /app/worker
COPY --from=builder /app/shared /app/shared
RUN pip install --no-cache-dir "celery[redis]" requests \
    opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp \
    opentelemetry-instrumentation-requests opentelemetry-instrumentation-logging
CMD ["celery", "-A", "celery_worker.celery_app", "worker", "--loglevel=info"]

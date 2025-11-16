FROM python:3.12-slim
WORKDIR /app/worker
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
COPY backend/worker /app/worker
RUN uv venv && . .venv/bin/activate && uv pip install "celery[redis]" requests
ENV PYTHONPATH=/app
CMD [".venv/bin/celery", "-A", "celery_worker.celery_app", "worker", "--loglevel=info"]

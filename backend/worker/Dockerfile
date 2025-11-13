FROM python:3.12-slim

WORKDIR /app/worker

COPY backend/worker /app/worker

RUN pip install --no-cache-dir "celery[redis]" requests

ENV PYTHONPATH=/app

CMD ["celery", "-A", "celery_worker.celery_app", "worker", "--loglevel=info"]

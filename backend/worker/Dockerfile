FROM python:3.12-slim

WORKDIR /app/worker

# Copy Celery worker code
COPY ./celery_worker.py /app/worker/celery_worker.py

# Install required Python dependencies for Celery + Redis and HTTP calls
RUN pip install --no-cache-dir "celery[redis]" requests

ENV PYTHONPATH=/app

# Default command runs the Celery worker
CMD ["celery", "-A", "celery_worker.celery_app", "worker", "--loglevel=info"]
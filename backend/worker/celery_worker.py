"""
Celery worker aligned with microservices architecture.

This worker offloads long-running ingestion by streaming files to the
chat_service HTTP endpoint instead of importing service code directly.
This keeps the worker lightweight and avoids heavy DB/vector dependencies.
"""

import os
from celery import Celery
import requests


BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")
CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL", "http://genai_chat_service:8003")

celery_app = Celery("worker", broker=BROKER_URL, backend=RESULT_BACKEND)


@celery_app.task(bind=True)
def long_ingest_task(self, filepath: str, uploaded_by: int):
    """
    Stream a local file to chat_service for ingestion.

    Expects the file to be present inside the worker container (e.g.,
    via a shared volume mounted at /data). Returns the chat_service JSON.
    """
    url = CHAT_SERVICE_URL.rstrip("/") + "/api/v1/ingest/upload"
    try:
        with open(filepath, "rb") as fh:
            files = {"file": (os.path.basename(filepath), fh)}
            data = {"user_id": str(uploaded_by)}
            resp = requests.post(url, files=files, data=data, timeout=120)
            resp.raise_for_status()
            return {"status": "accepted", "response": resp.json(), "filepath": filepath}
    except Exception as e:
        # Return a structured error for easier debugging
        return {"status": "error", "error": str(e), "filepath": filepath}

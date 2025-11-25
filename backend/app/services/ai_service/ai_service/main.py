"""
AI Service with LangSmith and OpenTelemetry
"""

from fastapi import FastAPI, UploadFile
import httpx
import os
from typing import Optional
from langsmith import traceable
from opentelemetry import trace
from shared.config import settings
from shared.logger import setup_observability, get_logger

# FastAPI app
app = FastAPI(title="AI Service")
setup_observability("ai_service", app)
logger = get_logger("ai_service")
otel_tracer = trace.get_tracer(__name__)

# OpenRouter config
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_API_BASE_URL", "https://openrouter.ai/api").rstrip("/")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
LLM_MODEL = getattr(settings, "OPENROUTER_MODEL", "openai/gpt-oss-20b:free")

def build_auth_headers() -> dict:
    headers = {"accept": "application/json", "content-type": "application/json"}
    if OPENROUTER_API_KEY:
        headers["Authorization"] = f"Bearer {OPENROUTER_API_KEY}"
        headers["X-Title"] = "GenAI Med Chat"
    return headers


# ====================== Generate Endpoint ======================
@app.post("/api/v1/generate")
@traceable
async def generate(payload: dict):
    with otel_tracer.start_as_current_span("ai_service.generate"):
        logger.info("ai_generate_received")
        messages = payload.get("messages") or ([{"role": "user", "content": payload.get("text")}] if payload.get("text") else [])
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                resp = await client.post(
                    f"{OPENROUTER_BASE_URL}/v1/chat/completions",
                    headers=build_auth_headers(),
                    json={"model": LLM_MODEL, "messages": messages},
                )
                resp.raise_for_status()
                data = resp.json()
                message = (data.get("choices", [{}])[0] or {}).get("message", {})
                return {"text": message.get("content", ""), "raw": data}
        except Exception:
            logger.exception("Generation failed")
            raise




# ====================== OCR Endpoint ======================
@app.post("/api/v1/ocr")
@traceable
async def ocr(file: UploadFile):
    with otel_tracer.start_as_current_span("ai_service.ocr"):
        content = await file.read()
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{OPENROUTER_BASE_URL}/v1/ocr",
                files={"file": (file.filename, content)},
                headers=build_auth_headers(),
            )
            resp.raise_for_status()
            return resp.json()


# ====================== Voice Endpoint ======================
@app.post("/api/v1/voice")
@traceable
async def voice(file: UploadFile):
    with otel_tracer.start_as_current_span("ai_service.voice"):
        content = await file.read()
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                f"{OPENROUTER_BASE_URL}/v1/voice",
                files={"file": (file.filename or "audio.webm", content)},
                headers=build_auth_headers(),
            )
            resp.raise_for_status()
            return resp.json()


# ====================== Embed Endpoint ======================
@app.post("/api/v1/embed")
@traceable
async def embed(payload: dict):
    with otel_tracer.start_as_current_span("ai_service.embed"):
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{OPENROUTER_BASE_URL}/v1/embed",
                json=payload,
                headers=build_auth_headers(),
            )
            resp.raise_for_status()
            return resp.json()

"""
AI Service with Ollama + LangChain + LangGraph + LangSmith
Includes basic endpoints for chat generation, OCR/voice passthrough, and RAG ingestion.
"""

from fastapi import FastAPI, UploadFile, Depends, Request
import httpx
import os
from typing import Optional
from langsmith import traceable
from opentelemetry import trace
from shared.logger import setup_observability, get_logger
from shared.config import settings

from .pipeline import ChatPipeline
from .rag import RAGStore
from .auth import get_current_user, require_role

# FastAPI app
app = FastAPI(title="AI Service")
setup_observability("ai_service", app)
logger = get_logger("ai_service")
otel_tracer = trace.get_tracer(__name__)

pipeline = ChatPipeline()
rag = RAGStore()


# ====================== Health ======================
@app.get("/ping")
def ping():
    return {"service": "ai_service", "status": "ok"}


# ====================== Chat (Ollama via LangChain/LangGraph) ======================
@app.post("/api/v1/generate")
@traceable
async def generate(payload: dict, request: Request):
    with otel_tracer.start_as_current_span("ai_service.generate"):
        text = payload.get("text") or ""
        # Try to decode user from Authorization header; fall back to payload or anonymous
        auth = request.headers.get("Authorization", "")
        user_id = payload.get("user_id") or "anonymous"
        if auth.startswith("Bearer "):
            try:
                from jose import jwt
                token = auth.split(" ", 1)[1]
                user = jwt.decode(token, os.getenv("SECRET_KEY", ""), algorithms=["HS256"]) or {}
                user_id = user.get("sub", user_id)
            except Exception:
                ...
        conv_id = payload.get("conv_id")
        logger.info("ai_generate_received")
        resp = pipeline.run(user_id=user_id, text=text, conv_id=conv_id)
        return resp


# ====================== OCR/Voice passthrough (to external provider if present) ======================
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_API_BASE_URL", "https://openrouter.ai/api").rstrip("/")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

def _headers() -> dict:
    h = {"accept": "application/json"}
    if OPENROUTER_API_KEY:
        h["Authorization"] = f"Bearer {OPENROUTER_API_KEY}"
        h["X-Title"] = "GenAI Med Chat"
    return h


@app.post("/api/v1/ocr")
@traceable
async def ocr(file: UploadFile):
    with otel_tracer.start_as_current_span("ai_service.ocr"):
        content = await file.read()
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{OPENROUTER_BASE_URL}/v1/ocr",
                files={"file": (file.filename, content)},
                headers=_headers(),
            )
            resp.raise_for_status()
            return resp.json()


@app.post("/api/v1/voice")
@traceable
async def voice(file: UploadFile):
    with otel_tracer.start_as_current_span("ai_service.voice"):
        content = await file.read()
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                f"{OPENROUTER_BASE_URL}/v1/voice",
                files={"file": (file.filename or "audio.webm", content)},
                headers=_headers(),
            )
            resp.raise_for_status()
            return resp.json()


# ====================== RAG Ingestion ======================
@app.post("/api/v1/index")
@traceable
async def index(payload: dict, _: dict = Depends(require_role("user"))):
    with otel_tracer.start_as_current_span("ai_service.index"):
        user_id = payload.get("user_id") or "anonymous"
        text = payload.get("text") or ""
        metadata = payload.get("metadata") or {}
        return rag.store_medical_doc(user_id=user_id, content=text, metadata=metadata)


@app.post("/api/v1/embed")
@traceable
async def embed(payload: dict):
    with otel_tracer.start_as_current_span("ai_service.embed"):
        text = payload.get("text") or ""
        if not text:
            return {"vector": [], "dim": 0}
        try:
            vec = rag.emb.embed_query(text)
            return {"vector": vec, "dim": len(vec)}
        except Exception:
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
                emb = HuggingFaceEmbeddings(model_name=model)
                vec = emb.embed_query(text)
                return {"vector": vec, "dim": len(vec)}
            except Exception as e:
                return {"error": str(e), "vector": [], "dim": 0}

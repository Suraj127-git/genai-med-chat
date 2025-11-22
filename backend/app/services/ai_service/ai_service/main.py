from fastapi import FastAPI, UploadFile
import httpx
from shared.config import settings
from shared.tracing import tracer

app = FastAPI(title="AI Service")

BASE = settings.AI_AGENT_BASE_URL.rstrip("/")
API_KEY = settings.AI_AGENT_API_KEY

def _headers():
    h = {"accept": "application/json"}
    if API_KEY:
        h["authorization"] = f"Bearer {API_KEY}"
    return h

@app.post("/api/v1/generate")
async def generate(payload: dict):
    t = tracer.trace("ai_service.generate")
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(f"{BASE}/v1/generate", json=payload, headers=_headers())
        r.raise_for_status()
        data = r.json()
        try:
            t.log({"input": payload, "output": data})
            t.end()
        except Exception:
            pass
        return data

@app.post("/api/v1/ocr")
async def ocr(file: UploadFile):
    t = tracer.trace("ai_service.ocr")
    async with httpx.AsyncClient(timeout=120.0) as client:
        body = await file.read()
        files = {"file": (file.filename or "image", body)}
        r = await client.post(f"{BASE}/v1/ocr", files=files, headers=_headers())
        r.raise_for_status()
        data = r.json()
        try:
            t.log({"filename": file.filename, "size": len(body), "output": data})
            t.end()
        except Exception:
            pass
        return data

@app.post("/api/v1/voice")
async def voice(file: UploadFile):
    t = tracer.trace("ai_service.voice")
    async with httpx.AsyncClient(timeout=180.0) as client:
        body = await file.read()
        files = {"file": (file.filename or "audio.webm", body)}
        r = await client.post(f"{BASE}/v1/voice", files=files, headers=_headers())
        r.raise_for_status()
        data = r.json()
        try:
            t.log({"filename": file.filename, "size": len(body), "output": data})
            t.end()
        except Exception:
            pass
        return data

@app.post("/api/v1/embed")
async def embed(payload: dict):
    t = tracer.trace("ai_service.embed")
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(f"{BASE}/v1/embed", json=payload, headers=_headers())
        r.raise_for_status()
        data = r.json()
        try:
            t.log({"input": payload, "output": data})
            t.end()
        except Exception:
            pass
        return data

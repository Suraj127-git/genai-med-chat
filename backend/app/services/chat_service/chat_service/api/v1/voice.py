from fastapi import APIRouter, UploadFile
import httpx
from shared.config import settings

router = APIRouter()


def _get_asr_pipeline():
    try:
        from transformers import pipeline
        return pipeline("automatic-speech-recognition", model="openai/whisper-small")
    except Exception:
        return None


@router.post("/voice")
async def transcribe_audio(file: UploadFile):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            files = {"file": (file.filename or "voice.webm", await file.read())}
            resp = await client.post(settings.AI_SERVICE_URL.rstrip("/") + "/api/v1/voice", files=files)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return {"text": "[ASR not available]"}
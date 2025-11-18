from fastapi import APIRouter, UploadFile
import httpx
from shared.config import settings

router = APIRouter()


def _get_trocr():
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
        model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
        return processor, model
    except Exception:
        return None, None


@router.post("/ocr")
async def extract_text(file: UploadFile):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            files = {"file": (file.filename or "image", await file.read())}
            resp = await client.post(settings.AI_SERVICE_URL.rstrip("/") + "/api/v1/ocr", files=files)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return {"text": "[OCR failed]"}
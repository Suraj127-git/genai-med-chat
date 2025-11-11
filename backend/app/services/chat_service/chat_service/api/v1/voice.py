from fastapi import APIRouter, UploadFile
import tempfile

router = APIRouter()


def _get_asr_pipeline():
    try:
        from transformers import pipeline
        return pipeline("automatic-speech-recognition", model="openai/whisper-small")
    except Exception:
        return None


@router.post("/voice")
async def transcribe_audio(file: UploadFile):
    asr = _get_asr_pipeline()
    if not asr:
        return {"text": "[ASR not available]"}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    text = asr(tmp_path)["text"]
    return {"text": text}
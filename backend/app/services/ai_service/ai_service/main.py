from fastapi import FastAPI, UploadFile
import tempfile
from shared.config import settings

app = FastAPI(title="AI Service")

def _get_text_generation():
    try:
        from transformers import pipeline
        return pipeline("text-generation", model=settings.HF_MODEL)
    except Exception:
        return None

def _get_trocr():
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
        model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")
        return processor, model
    except Exception:
        return None, None

def _get_asr():
    try:
        from transformers import pipeline
        return pipeline("automatic-speech-recognition", model="openai/whisper-small")
    except Exception:
        return None

def _get_embedder():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(settings.EMBEDDING_MODEL)
    except Exception:
        return None

@app.post("/api/v1/generate")
async def generate(payload: dict):
    text = payload.get("text", "")
    gen = _get_text_generation()
    if not gen:
        return {"text": "[generation not available]"}
    out = gen(text, max_length=256, do_sample=True)
    t = out[0]["generated_text"] if isinstance(out, list) and out else str(out)
    return {"text": t}

@app.post("/api/v1/ocr")
async def ocr(file: UploadFile):
    processor, model = _get_trocr()
    if not processor or not model:
        return {"text": "[OCR not available]"}
    try:
        from PIL import Image
        image = Image.open(file.file).convert("RGB")
        pixel_values = processor(images=image, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return {"text": text}
    except Exception:
        return {"text": "[OCR failed]"}

@app.post("/api/v1/voice")
async def voice(file: UploadFile):
    asr = _get_asr()
    if not asr:
        return {"text": "[ASR not available]"}
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    text = asr(tmp_path)["text"]
    return {"text": text}

@app.post("/api/v1/embed")
async def embed(payload: dict):
    text = payload.get("text", "")
    embedder = _get_embedder()
    if not embedder:
        return {"vector": []}
    vec = embedder.encode(text)
    return {"vector": list(map(float, vec))}
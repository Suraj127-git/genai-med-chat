from fastapi import APIRouter, UploadFile

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
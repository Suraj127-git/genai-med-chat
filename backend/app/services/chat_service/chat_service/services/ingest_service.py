from pathlib import Path
from uuid import uuid4
from shared.config import settings

# optional OCR libraries will be used if installed
try:
    import pytesseract
    from PIL import Image
except Exception:
    pytesseract = None
    Image = None

# langchain utilities if available
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import Qdrant
except Exception:
    RecursiveCharacterTextSplitter = None
    HuggingFaceEmbeddings = None
    Qdrant = None


class IngestService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.qdrant = None
        if Qdrant and HuggingFaceEmbeddings:
            try:
                emb = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
                self.qdrant = Qdrant(url=settings.QDRANT_URL, prefer_grpc=False, collection_name=settings.QDRANT_COLLECTION)
            except Exception:
                self.qdrant = None

    async def save_upload(self, file, uploaded_by: int) -> str:
        ext = Path(file.filename).suffix or ""
        fname = f"{uuid4().hex}{ext}"
        dest = self.upload_dir / fname
        contents = await file.read()
        with open(dest, "wb") as f:
            f.write(contents)
        return str(dest)

    def _extract_text(self, filepath: str) -> str:
        # basic extraction: if image and pytesseract available, OCR; else read as text
        p = Path(filepath)
        try:
            if Image and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"} and pytesseract:
                img = Image.open(filepath)
                return pytesseract.image_to_string(img)
        except Exception:
            pass
        try:
            return Path(filepath).read_text(errors="ignore")
        except Exception:
            return ""

    def ingest_file(self, filepath: str, uploaded_by: int):
        text = self._extract_text(filepath)
        if not text:
            return
        if RecursiveCharacterTextSplitter and self.qdrant:
            splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
            docs = splitter.split_text(text)
            embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
            try:
                self.qdrant.upsert(
                    points=[{"id": uuid4().hex, "vector": embeddings.embed_query(d), "payload": {"source": filepath}} for d in docs]
                )
            except Exception:
                pass
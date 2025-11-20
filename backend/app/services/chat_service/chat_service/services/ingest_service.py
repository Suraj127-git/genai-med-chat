from pathlib import Path
from uuid import uuid4
from shared.config import settings
import httpx

# optional OCR libraries will be used if installed
Image = None

# langchain utilities if available
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.vectorstores import Qdrant
except Exception:
    RecursiveCharacterTextSplitter = None
    Qdrant = None


class IngestService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.qdrant = None
        if Qdrant:
            try:
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
        # basic extraction: read as text only; images handled via dedicated OCR endpoint
        p = Path(filepath)
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
            try:
                vectors = []
                with httpx.Client(timeout=30.0) as client:
                    for d in docs:
                        r = client.post(settings.AI_SERVICE_URL.rstrip("/") + "/api/v1/embed", json={"text": d})
                        v = r.json().get("vector", [])
                        vectors.append(v)
                self.qdrant.upsert(points=[{"id": uuid4().hex, "vector": v, "payload": {"source": filepath}} for v in vectors])
            except Exception:
                pass
from typing import Optional, List, Dict, Any
import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from langchain_community.vectorstores import Qdrant as LCQdrant
from langchain_community.embeddings import HuggingFaceEmbeddings

from .security import encrypt_medical
from shared.mongo import get_db


class RAGStore:
    def __init__(self):
        self.mongo = get_db()
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.collection = os.getenv("QDRANT_COLLECTION", "docs")
        self.emb_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self._ensure_qdrant()
        self.emb = HuggingFaceEmbeddings(model_name=self.emb_model)
        self.vs = LCQdrant(
            url=self.qdrant_url,
            prefer_grpc=False,
            collection_name=self.collection,
            embeddings=self.emb,
        )

    def _ensure_qdrant(self):
        try:
            client = QdrantClient(url=self.qdrant_url)
            collections = client.get_collections().collections
            names = {c.name for c in collections}
            if self.collection not in names:
                client.create_collection(
                    collection_name=self.collection,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
        except Exception:
            pass

    def store_medical_doc(self, user_id: str, content: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        try:
            b = content.encode("utf-8")
            enc = encrypt_medical(b)
            doc = {
                "user_id": user_id,
                "data": enc,
                "encrypted": True,
                "metadata": metadata or {},
            }
            res = self.mongo["medical_data"].insert_one(doc)
            # index into qdrant for semantic search
            self.vs.add_texts([content], metadatas=[{"user_id": user_id, **(metadata or {})}], ids=[str(res.inserted_id)])
            return {"id": str(res.inserted_id)}
        except Exception as e:
            return {"error": str(e)}

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        try:
            retriever = self.vs.as_retriever(search_type="mmr", search_kwargs={"k": top_k})
            docs = retriever.get_relevant_documents(query)
            out: List[Dict[str, Any]] = []
            for d in docs:
                out.append({
                    "text": getattr(d, "page_content", ""),
                    "metadata": getattr(d, "metadata", {}),
                })
            return out
        except Exception:
            return []

    def get_history(self, conv_id: Optional[str]) -> List[Dict[str, Any]]:
        if not conv_id:
            return []
        return list(self.mongo["messages"].find({"conv_id": conv_id}, sort=[("_id", 1)]))


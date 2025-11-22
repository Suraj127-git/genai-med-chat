import asyncio
from typing import Dict, Any

import httpx
from shared.mongo_repo import MongoRepo
from shared.config import settings
from shared.tracing import tracer

# Optional langchain imports (if installed)
try:
    from langchain.chains import RetrievalQA
    from langchain.vectorstores import Qdrant
    from langchain.embeddings import HuggingFaceEmbeddings
except Exception:
    Qdrant = None
    RetrievalQA = None
    HuggingFaceEmbeddings = None


class ChatService:
    def __init__(self):
        self.repo = MongoRepo()
        self._init_rag()

    def _init_rag(self):
        if Qdrant and HuggingFaceEmbeddings:
            try:
                emb = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
                self.vs = Qdrant(url=settings.QDRANT_URL, prefer_grpc=False, collection_name=settings.QDRANT_COLLECTION)
                retriever = self.vs.as_retriever(search_type="mmr", search_kwargs={"k": 3})
                self.rqa = RetrievalQA.from_chain_type(llm=self.model.llm, chain_type="stuff", retriever=retriever)
            except Exception:
                self.vs = None
                self.rqa = None
        else:
            self.vs = None
            self.rqa = None

    async def handle_query(self, user_id: int, text: str, modalities: Dict | None = None) -> Dict[str, Any]:
        t = tracer.trace("chat_service.handle_query")
        modalities = modalities or {}
        sources: list[Any] = []

        try:
            conv_id = self.repo.create_conversation(user_id=user_id, title=(text[:50] + "..."))
        except Exception:
            conv_id = None

        from .langgraph_service import LangGraphService
        lg = LangGraphService()

        user_node_id = None
        if conv_id is not None:
            user_node_id = lg.record_node(conv_id=conv_id, node_type="user", content=text, metadata={"user_id": user_id})

        retrieval_node_ids: list[int] = []
        retrieval_texts: list[str] = []
        if getattr(self, "rqa", None):
            try:
                loop = asyncio.get_event_loop()
                rqa_output = await loop.run_in_executor(None, lambda: self.rqa.run(text))
                try:
                    retriever = self.vs.as_retriever(search_type="mmr", search_kwargs={"k": 3})
                    docs = retriever.get_relevant_documents(text)
                except Exception:
                    docs = []
                for d in docs:
                    content_snippet = (d.page_content[:400] if hasattr(d, "page_content") else str(d))
                    nid = lg.record_node(conv_id=conv_id, node_type="retrieval", content=content_snippet, metadata={"source": getattr(d, "metadata", {})})
                    retrieval_node_ids.append(nid)
                    retrieval_texts.append(content_snippet)
                    sources.append(getattr(d, "metadata", {}))
            except Exception:
                pass

        answer = None
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(settings.AI_SERVICE_URL.rstrip("/") + "/api/v1/generate", json={"text": text})
                resp.raise_for_status()
                answer = resp.json().get("text")
        except Exception:
            answer = "Sorry — model generation failed."

        gen_node_id = None
        if conv_id is not None:
            gen_node_id = lg.record_node(conv_id=conv_id, node_type="generation", content=answer, metadata={"sources": sources})

        try:
            if conv_id is not None and user_node_id:
                if gen_node_id:
                    lg.record_edge(conv_id=conv_id, from_node=user_node_id, to_node=gen_node_id, relation="asked_for")
                for r_nid in retrieval_node_ids:
                    lg.record_edge(conv_id=conv_id, from_node=user_node_id, to_node=r_nid, relation="retrieved")
                    if gen_node_id:
                        lg.record_edge(conv_id=conv_id, from_node=r_nid, to_node=gen_node_id, relation="informed")
        except Exception:
            pass

        try:
            self.repo.create_message(conv_id=conv_id, sender="user", content=text, metadata={"user_id": user_id})
            self.repo.create_message(conv_id=conv_id, sender="bot", content=answer, metadata={"sources": sources})
        except Exception:
            pass

        try:
            t.log({"user_id": user_id, "text": text, "answer": answer, "conv_id": conv_id, "sources": sources})
            t.end()
        except Exception:
            pass
        return {"answer": answer, "sources": sources, "conv_id": conv_id}

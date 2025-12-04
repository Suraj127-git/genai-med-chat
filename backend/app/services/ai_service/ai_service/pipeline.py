from typing import Dict, Any, Optional, List
import os
from cachetools import LRUCache

from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import ChatOllama
from langgraph.graph import StateGraph

from .rag import RAGStore


class ConversationState(dict):
    user_id: str
    text: str
    conv_id: Optional[str]
    context_docs: List[Dict[str, Any]]
    answer: Optional[str]
    sources: List[Dict[str, Any]]


class ChatPipeline:
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_URL", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
        self.memory = ConversationBufferMemory(return_messages=True)
        self.llm = ChatOllama(base_url=self.ollama_url, model=self.ollama_model)
        self.rag = RAGStore()
        self.cache = LRUCache(maxsize=256)
        self._build_graph()

    def _retrieve(self, state: ConversationState) -> ConversationState:
        docs = self.rag.search(state["text"], top_k=3)
        state["context_docs"] = docs
        state["sources"] = docs
        return state

    def _generate(self, state: ConversationState) -> ConversationState:
        key = (state["text"], tuple(sorted([d.get("text", "")[:64] for d in state.get("context_docs", [])])))
        if key in self.cache:
            state["answer"] = self.cache[key]
            return state
        messages = []
        for m in (self.memory.chat_memory.messages or []):
            messages.append(m)
        # System prompt with lightweight RAG context
        context = "\n\n".join([d.get("text", "") for d in state.get("context_docs", [])])
        prompt = f"You are a medical assistant. Use the following context if relevant:\n{context}\n\nUser: {state['text']}"
        messages.append(HumanMessage(content=prompt))
        resp = self.llm.invoke(messages)
        answer = resp.content if hasattr(resp, "content") else str(resp)
        self.memory.chat_memory.add_message(HumanMessage(content=state["text"]))
        self.memory.chat_memory.add_message(AIMessage(content=answer))
        self.cache[key] = answer
        state["answer"] = answer
        return state

    def _persist(self, state: ConversationState) -> ConversationState:
        # Minimal persistence handled by ChatService; AI service persists medical docs when ingested
        return state

    def _build_graph(self):
        g = StateGraph(ConversationState)
        g.add_node("retrieve", self._retrieve)
        g.add_node("generate", self._generate)
        g.add_node("persist", self._persist)
        g.set_entry_point("retrieve")
        g.add_edge("retrieve", "generate")
        g.add_edge("generate", "persist")
        self.graph = g.compile()

    def run(self, user_id: str, text: str, conv_id: Optional[str] = None) -> Dict[str, Any]:
        initial: ConversationState = {
            "user_id": user_id,
            "text": text,
            "conv_id": conv_id,
            "context_docs": [],
            "answer": None,
            "sources": [],
        }
        result = self.graph.invoke(initial)
        return {"text": result.get("answer"), "sources": result.get("sources", [])}


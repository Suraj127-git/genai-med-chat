import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient


def resolve_chat_service_app():
    """Import chat_service FastAPI app from available location."""
    backend_dir = Path(__file__).resolve().parents[1]
    candidates = [
        backend_dir / "microservices-python" / "services" / "chat_service",
        backend_dir / "app" / "services" / "chat_service",
    ]
    for cand in candidates:
        if cand.exists():
            sys.path.append(str(cand))
            try:
                mod = __import__("chat_service.main", fromlist=["app"])
                return mod.app
            except Exception:
                continue
    raise RuntimeError("Could not locate chat_service.main app module")


@pytest.fixture(scope="module")
def app():
    return resolve_chat_service_app()


@pytest.fixture
def client(app):
    return TestClient(app)


class FakeRepo:
    """In-memory stub for MySQLRepo used by ChatService and LangGraphService."""
    def __init__(self):
        self.conv_seq = 100
        self.messages = []
        self.nodes = []
        self.edges = []

    def create_conversation(self, user_id: int, title: str = None):
        self.conv_seq += 1
        return self.conv_seq

    def create_message(self, conv_id, sender, content, metadata=None):
        self.messages.append({"conv_id": conv_id, "sender": sender, "content": content, "metadata": metadata or {}})
        return len(self.messages)

    def create_graph_node(self, conv_id: int, node_type: str, content: str, metadata: dict = None):
        node_id = len(self.nodes) + 1
        self.nodes.append({"id": node_id, "conv_id": conv_id, "node_type": node_type, "content": content, "metadata": metadata or {}})
        return node_id

    def create_graph_edge(self, conv_id: int, from_node: int, to_node: int, relation: str, metadata: dict = None):
        edge_id = len(self.edges) + 1
        self.edges.append({"id": edge_id, "conv_id": conv_id, "from_node": from_node, "to_node": to_node, "relation": relation, "metadata": metadata or {}})
        return edge_id

    def get_graph(self, conv_id: int):
        return {
            "nodes": [n for n in self.nodes if n["conv_id"] == conv_id],
            "edges": [e for e in self.edges if e["conv_id"] == conv_id],
        }


@pytest.fixture(autouse=True)
def monkeypatch_repos(monkeypatch):
    """Patch repo usages to avoid external DB and vector deps."""
    import chat_service.api.v1.chat as chat_router
    chat_router.chat_service.repo = FakeRepo()

    import chat_service.services.langgraph_service as lg_mod

    class FakeLangGraphService:
        def __init__(self):
            self.repo = chat_router.chat_service.repo

        def record_node(self, conv_id: int, node_type: str, content: str, metadata: dict | None = None):
            return self.repo.create_graph_node(conv_id, node_type, content, metadata)

        def record_edge(self, conv_id: int, from_node: int, to_node: int, relation: str, metadata: dict | None = None):
            return self.repo.create_graph_edge(conv_id, from_node, to_node, relation, metadata)

        def get_graph(self, conv_id: int):
            return self.repo.get_graph(conv_id)

    monkeypatch.setattr(lg_mod, "LangGraphService", FakeLangGraphService)
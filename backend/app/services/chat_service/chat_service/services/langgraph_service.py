from typing import Dict, Any, Optional

try:
    import langgraph  # optional
    HAS_LANGGRAPH = True
except Exception:
    HAS_LANGGRAPH = False

try:
    from shared.mongo_repo import MongoRepo
    HAS_MONGO = True
except Exception:
    HAS_MONGO = False


class LangGraphService:
    def __init__(self):
        self.repo = MongoRepo() if HAS_MONGO else None
        self.use_langgraph = HAS_LANGGRAPH
        if self.use_langgraph:
            try:
                self.client = langgraph.Client()
            except Exception:
                self.client = None
                self.use_langgraph = False

    def record_node(self, conv_id: str, node_type: str, content: str, metadata: Dict[str, Any] | None = None) -> Optional[int]:
        try:
            if self.repo:
                return self.repo.create_graph_node(conv_id=conv_id, node_type=node_type, content=content, metadata=metadata or {})
        except Exception:
            pass
        return None

    def record_edge(self, conv_id: str, from_node: int, to_node: int, relation: str, metadata: Dict[str, Any] | None = None) -> Optional[int]:
        try:
            if self.repo:
                return self.repo.create_graph_edge(conv_id=conv_id, from_node=from_node, to_node=to_node, relation=relation, metadata=metadata or {})
        except Exception:
            pass
        return None

    def get_graph(self, conv_id: str):
        if self.use_langgraph and getattr(self, "client", None):
            # TODO: fetch from langgraph client and convert to dict
            pass
        if self.repo:
            return self.repo.get_graph(conv_id)
        return {"nodes": [], "edges": []}

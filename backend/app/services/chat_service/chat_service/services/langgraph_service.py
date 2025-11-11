from typing import Dict, Any, Optional

try:
    import langgraph  # optional
    HAS_LANGGRAPH = True
except Exception:
    HAS_LANGGRAPH = False

from shared.mysql_repo import MySQLRepo


class LangGraphService:
    def __init__(self):
        self.repo = MySQLRepo()
        self.use_langgraph = HAS_LANGGRAPH
        if self.use_langgraph:
            try:
                self.client = langgraph.Client()
            except Exception:
                self.client = None
                self.use_langgraph = False

    def record_node(self, conv_id: int, node_type: str, content: str, metadata: Dict[str, Any] | None = None) -> Optional[int]:
        try:
            return self.repo.create_graph_node(conv_id=conv_id, node_type=node_type, content=content, metadata=metadata or {})
        except Exception:
            return None

    def record_edge(self, conv_id: int, from_node: int, to_node: int, relation: str, metadata: Dict[str, Any] | None = None) -> Optional[int]:
        try:
            return self.repo.create_graph_edge(conv_id=conv_id, from_node=from_node, to_node=to_node, relation=relation, metadata=metadata or {})
        except Exception:
            return None

    def get_graph(self, conv_id: int):
        if self.use_langgraph and getattr(self, "client", None):
            # TODO: fetch from langgraph client and convert to dict
            pass
        return self.repo.get_graph(conv_id)
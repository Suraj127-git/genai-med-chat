from typing import Dict, Any
from .mongo import get_db


class MongoRepo:
    def __init__(self):
        self.db = get_db()
        self.users = self.db["users"]
        self.conversations = self.db["conversations"]
        self.messages = self.db["messages"]
        self.graph_nodes = self.db["graph_nodes"]
        self.graph_edges = self.db["graph_edges"]

    def create_user(self, username: str, email: str, password_hash: str, role: str = "user") -> str:
        doc = {"username": username, "email": email, "password_hash": password_hash, "role": role}
        res = self.users.insert_one(doc)
        return str(res.inserted_id)

    def create_conversation(self, user_id: str, title: str | None = None) -> str:
        doc = {"user_id": user_id, "title": title}
        res = self.conversations.insert_one(doc)
        return str(res.inserted_id)

    def create_message(self, conv_id: str, sender: str, content: str, metadata: Dict[str, Any] | None = None) -> str:
        doc = {"conv_id": conv_id, "sender": sender, "content": content, "metadata": metadata or {}}
        res = self.messages.insert_one(doc)
        return str(res.inserted_id)

    def create_graph_node(self, conv_id: str, node_type: str, content: str, metadata: Dict[str, Any] | None = None) -> str:
        doc = {"conv_id": conv_id, "node_type": node_type, "content": content, "metadata": metadata or {}}
        res = self.graph_nodes.insert_one(doc)
        return str(res.inserted_id)

    def create_graph_edge(self, conv_id: str, from_node: str, to_node: str, relation: str, metadata: Dict[str, Any] | None = None) -> str:
        doc = {"conv_id": conv_id, "from_node": from_node, "to_node": to_node, "relation": relation, "metadata": metadata or {}}
        res = self.graph_edges.insert_one(doc)
        return str(res.inserted_id)

    def get_graph(self, conv_id: str):
        nodes = list(self.graph_nodes.find({"conv_id": conv_id}, {"_id": 0}))
        edges = list(self.graph_edges.find({"conv_id": conv_id}, {"_id": 0}))
        return {"nodes": nodes, "edges": edges}

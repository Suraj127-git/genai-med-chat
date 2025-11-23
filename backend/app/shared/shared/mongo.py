from pymongo import MongoClient
import os

_client = None

def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI", "mongodb://genai_mongo:27017")
        _client = MongoClient(uri)
    return _client

def get_db(name: str = None):
    client = get_mongo_client()
    db_name = name or os.getenv("MONGO_DB", "genai_med")
    return client[db_name]

def init_db(db=None):
    d = db or get_db()
    d["users"].create_index("email", unique=True)
    d["users"].create_index("username", unique=True)
    d["conversations"].create_index("user_id")
    d["messages"].create_index("conv_id")
    d["graph_nodes"].create_index("conv_id")
    d["graph_edges"].create_index("conv_id")
    d["graph_edges"].create_index([("from_node", 1), ("to_node", 1)])

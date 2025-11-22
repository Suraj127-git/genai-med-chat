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

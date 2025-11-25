import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "genai-med-chat"

    # # MySQL (change credentials for local)
    # MYSQL_HOST: str = os.getenv("MYSQL_HOST", "mysql")
    # MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    # MYSQL_USER: str = os.getenv("MYSQL_USER", "genai")
    # MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "genai")
    # MYSQL_DB: str = os.getenv("MYSQL_DB", "genai_med")
    # MYSQL_DSN: str = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"

    # MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://genai_mongo:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "genai_med")

    # Qdrant
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "docs")

    # Models & embeddings
    MODEL_BACKEND: str = os.getenv("MODEL_BACKEND", "hf")  # hf or ollama
    HF_MODEL: str = os.getenv("HF_MODEL", "gpt2")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "http://localhost:8004")
    AI_AGENT_BASE_URL: str = os.getenv("AI_AGENT_BASE_URL", "https://openrouter.ai/api")
    AI_AGENT_API_KEY: str = os.getenv("AI_AGENT_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")

    # Uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/data/uploads")

    # Misc
    CORS_ORIGINS: list = ["*"]


settings = Settings()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.logger import get_logger
from shared.mongo import get_db
from shared.config import settings

from user_service.api import auth
from datetime import datetime

app = FastAPI(title="User Service")
logger = get_logger(__name__)
db = get_db()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/ping")
async def ping():
    try:
        db.command("ping")
        return {"service": "user", "status": "ok", "db": {"connected": True}}
    except Exception as e:
        return {"service": "user", "status": "error", "db": {"connected": False, "error": str(e)}}

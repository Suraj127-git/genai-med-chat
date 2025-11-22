from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.logger import get_logger
from shared.database import Database
from shared.config import settings

from user_service.api import auth
from user_service import models

app = FastAPI(title="User Service")
logger = get_logger(__name__)
db = Database()

# Initialize database tables
models.User.metadata.create_all(bind=db.engine)

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
    return {"service": "user", "status": "ok", "db": db.status()}
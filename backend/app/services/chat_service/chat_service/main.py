from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config import settings
from shared.logger import setup_observability
from chat_service.api.v1 import chat, ingest, voice, ocr, graph


app = FastAPI(title="Chat Service")
setup_observability("chat_service", app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["ingest"])
app.include_router(voice.router, prefix="/api/v1", tags=["voice"])
app.include_router(ocr.router, prefix="/api/v1", tags=["ocr"])
app.include_router(graph.router, prefix="/api/v1", tags=["graph"])


@app.get("/")
def root():
    return {"service": "chat_service"}

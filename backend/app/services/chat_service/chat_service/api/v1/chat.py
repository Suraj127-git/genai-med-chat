from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

from chat_service.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


class ChatRequest(BaseModel):
    user_id: int
    text: str
    modalities: Optional[Dict] = None


class ChatResponse(BaseModel):
    answer: str
    sources: Optional[list] = []


@router.post("/query", response_model=ChatResponse)
async def query(req: ChatRequest, bg: BackgroundTasks):
    if not req.text:
        raise HTTPException(status_code=400, detail="text required")
    resp = await chat_service.handle_query(req.user_id, req.text, modalities=req.modalities or {})
    return resp
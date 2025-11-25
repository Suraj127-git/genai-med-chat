from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict

from chat_service.services.chat_service import ChatService
from chat_service.core.auth import get_current_user

router = APIRouter()
chat_service = ChatService()


class ChatRequest(BaseModel):
    text: str
    modalities: Optional[Dict] = None


class ChatResponse(BaseModel):
    answer: str
    sources: Optional[list] = []


@router.post("/query", response_model=ChatResponse)
async def query(req: ChatRequest, bg: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    if not req.text:
        raise HTTPException(status_code=400, detail="text required")
    resp = await chat_service.handle_query(current_user["id"], req.text, modalities=req.modalities or {})
    return resp

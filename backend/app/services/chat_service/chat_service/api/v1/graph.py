from fastapi import APIRouter, HTTPException

from chat_service.services.langgraph_service import LangGraphService

router = APIRouter()


@router.get("/graph/{conv_id}")
def get_graph(conv_id: int):
    lg = LangGraphService()
    g = lg.get_graph(conv_id)
    if not g:
        raise HTTPException(status_code=404, detail="No graph found")
    return g
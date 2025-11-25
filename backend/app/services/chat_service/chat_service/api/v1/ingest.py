from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse

from chat_service.services.ingest_service import IngestService
from chat_service.core.auth import get_current_user

router = APIRouter()
ingest_service = IngestService()


@router.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if file.filename == "":
        raise HTTPException(status_code=400, detail="file required")
    saved_path = await ingest_service.save_upload(file, uploaded_by=current_user["id"])
    background_tasks.add_task(ingest_service.ingest_file, saved_path, current_user["id"]) 
    return JSONResponse({"status": "accepted", "filepath": saved_path}, status_code=202)

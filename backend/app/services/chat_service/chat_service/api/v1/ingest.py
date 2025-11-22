from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from chat_service.services.ingest_service import IngestService

router = APIRouter()
ingest_service = IngestService()


@router.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...), user_id: int = Form(...)):
    if file.filename == "":
        raise HTTPException(status_code=400, detail="file required")
    saved_path = await ingest_service.save_upload(file, uploaded_by=user_id)
    background_tasks.add_task(ingest_service.ingest_file, saved_path, user_id)
    return JSONResponse({"status": "accepted", "filepath": saved_path}, status_code=202)
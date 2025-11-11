from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException

from chat_service.services.ingest_service import IngestService

router = APIRouter()
ingest_service = IngestService()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), user_id: int = Form(...), bg: BackgroundTasks | None = None):
    if file.filename == "":
        raise HTTPException(status_code=400, detail="file required")
    saved_path = await ingest_service.save_upload(file, uploaded_by=user_id)
    if bg:
        bg.add_task(ingest_service.ingest_file, saved_path, user_id)
        return {"status": "accepted", "filepath": saved_path}
    else:
        ingest_service.ingest_file(saved_path, user_id)
        return {"status": "ingested", "filepath": saved_path}
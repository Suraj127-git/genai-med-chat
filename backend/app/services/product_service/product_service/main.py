from fastapi import FastAPI
from shared.logger import get_logger
from shared.mongo import get_db


app = FastAPI(title="Product Service")
logger = get_logger(__name__)
db = get_db()


@app.get("/ping")
async def ping():
    try:
        db.command("ping")
        return {"service": "product", "status": "ok", "db": {"connected": True}}
    except Exception as e:
        return {"service": "product", "status": "error", "db": {"connected": False, "error": str(e)}}

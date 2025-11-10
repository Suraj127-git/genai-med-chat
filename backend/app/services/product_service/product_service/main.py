from fastapi import FastAPI
from shared.logger import get_logger
from shared.database import Database


app = FastAPI(title="Product Service")
logger = get_logger(__name__)
db = Database()


@app.get("/ping")
async def ping():
    return {"service": "product", "status": "ok", "db": db.status()}
from fastapi import FastAPI, Request, Response
import httpx
from shared.logger import get_logger


app = FastAPI(title="Gateway")
logger = get_logger(__name__)


async def proxy_request(target_base: str, path: str, request: Request) -> Response:
    url = f"{target_base}/{path}" if path else target_base
    headers = dict(request.headers)
    body = await request.body()
    method = request.method
    params = dict(request.query_params)

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.request(method, url, params=params, headers=headers, content=body)

    # Preserve content-type if available
    media_type = resp.headers.get("content-type")
    return Response(content=resp.content, status_code=resp.status_code, media_type=media_type)


@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_users(path: str, request: Request):
    logger.info(f"Proxying to user_service: {path}")
    return await proxy_request("http://localhost:8001", path, request)


@app.api_route("/products/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_products(path: str, request: Request):
    logger.info(f"Proxying to product_service: {path}")
    return await proxy_request("http://localhost:8002", path, request)


@app.get("/ping")
async def ping():
    return {"gateway": "ok"}


@app.api_route("/chat/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_chat(path: str, request: Request):
    logger.info(f"Proxying to chat_service: {path}")
    # Chat service mounts routers under /api/v1/chat
    return await proxy_request("http://localhost:8003/api/v1/chat", path, request)
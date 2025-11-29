from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx
from shared.logger import get_logger, setup_observability
from shared.config import settings


app = FastAPI(title="Gateway")
setup_observability("gateway", app)
logger = get_logger(__name__)

CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL", "http://chat-service:8003").rstrip("/")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8001").rstrip("/")


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


@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_auth(path: str, request: Request):
    logger.info(f"Proxying to user_service/auth: {path}")
    return await proxy_request(f"{USER_SERVICE_URL}/auth", path, request)


@app.api_route("/users/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_users(path: str, request: Request):
    logger.info(f"Proxying to user_service: {path}")
    return await proxy_request(USER_SERVICE_URL, path, request)


@app.get("/ping")
async def ping():
    return {"gateway": "ok"}


@app.api_route("/chat/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_chat(path: str, request: Request):
    logger.info(f"Proxying to chat_service: {path}")
    return await proxy_request(f"{CHAT_SERVICE_URL}/api/v1/chat", path, request)


@app.api_route("/api/v1/chat/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_chat_api(path: str, request: Request):
    logger.info(f"Proxying to chat_service /api/v1/chat: {path}")
    return await proxy_request(f"{CHAT_SERVICE_URL}/api/v1/chat", path, request)


@app.api_route("/api/v1/graph/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_graph(path: str, request: Request):
    logger.info(f"Proxying to chat_service /api/v1/graph: {path}")
    return await proxy_request(f"{CHAT_SERVICE_URL}/api/v1/graph", path, request)


@app.api_route("/api/v1/voice", methods=["POST"])  # file upload
async def proxy_voice(request: Request):
    logger.info("Proxying to chat_service /api/v1/voice")
    return await proxy_request(f"{CHAT_SERVICE_URL}/api/v1/voice", "", request)


@app.api_route("/api/v1/ocr", methods=["POST"])  # file upload
async def proxy_ocr(request: Request):
    logger.info("Proxying to chat_service /api/v1/ocr")
    return await proxy_request(f"{CHAT_SERVICE_URL}/api/v1/ocr", "", request)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if hasattr(settings, 'CORS_ORIGINS') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

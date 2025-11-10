# genai-med-chat (microservices)
This project now runs a Python microservices backend alongside local infra (MySQL, Redis, Qdrant). The monolith FastAPI app has been removed in favor of services.

## Infra
- Start infra containers: see `infra/docker-compose.yml`. It includes MySQL, Redis, Qdrant, phpMyAdmin, and Frontend. The monolith backend service has been removed.
- Initialize DB tables: `python backend/scripts/init_db.py` (uses shared SQLAlchemy metadata).

## Backend Microservices
- Requirements: install `poetry`.
- Navigate to `backend/microservices-python` and run:
  - `make install` (installs shared and services)
  - `make run-gateway` (FastAPI, port `8000`)
  - `make run-user` (FastAPI, port `8001`)
  - `make run-product` (FastAPI, port `8002`)
  - `make run-chat` (FastAPI, port `8003`)

### Gateway
- Proxies requests:
  - `/users/*` -> `user_service` (port 8001)
  - `/products/*` -> `product_service` (port 8002)
  - `/chat/*` -> `chat_service` (port 8003, base `/api/v1/chat`)

### Chat Service Endpoints
- `POST /api/v1/chat/query` — chat with the assistant
- `POST /api/v1/ingest/upload` — upload a document for ingestion
- `POST /api/v1/voice` — speech-to-text (optional deps)
- `POST /api/v1/ocr` — OCR for images (optional deps)
- `GET /api/v1/graph/{conv_id}` — conversation graph

### Scripts
- Ingest document via service: `python backend/scripts/ingest_documents.py <filepath> --user-id 0 --mode http`
  - Defaults to HTTP mode posting to `http://localhost:8003/api/v1/ingest/upload`
  - Use `--mode local` to attempt direct import fallback

## Testing
- Minimal test for chat_service exists at `backend/microservices-python/services/chat_service/tests/test_chat_api.py`.

# GenAI Medical Chat — Microservices Platform

## 1. Project Overview
- Purpose: AI‑powered medical assistant that streamlines intake, triage, and patient guidance across text, voice, and document modalities. It reduces clinician workload, accelerates information gathering, and improves care quality through secure retrieval‑augmented generation.
- Business Value:
  - Faster intake and triage with structured conversation flows and document OCR.
  - Consistent patient experience with secure, auditable interactions.
  - Scalable architecture suited for regulated environments with observability and role‑based access.
- Key Features:
  - Secure authentication and JWT‑based session management.
  - Conversational assistant with RAG context from ingested medical documents.
  - Voice input (ASR) and OCR ingestion for images.
  - Conversation graph visualization of retrieval and generation steps.
  - End‑to‑end observability (traces, metrics, logs) ready for SRE.
- Technology Stack:
  - Backend: Python, FastAPI, httpx, Celery, OpenTelemetry
  - AI/RAG: LangChain, LangGraph, Sentence Transformers, Qdrant
  - Data Stores: MongoDB (users, messages, graphs), Qdrant (vectors), Redis (queues)
  - Frontend: React, Vite, Redux Toolkit, TailwindCSS
  - Ops: Docker Compose, k3s + Helm (Ingress via Traefik), Grafana/Prometheus/Loki/Tempo


## 2. Setup Instructions
- Environment Requirements:
  - Python 3.12+, Node.js 20+, Docker/Docker Compose
  - Optional: k3s + Helm for Kubernetes deployments
  - External GPU Ollama server (recommended) for high‑throughput model serving
- Configuration:
  - Backend env variables (see `backend/app/shared/config.py:1`):
    - `MONGO_URI`, `MONGO_DB`, `QDRANT_URL`, `QDRANT_COLLECTION`
    - `AI_SERVICE_URL`, `EMBEDDING_MODEL`, `OLLAMA_URL`, `OLLAMA_MODEL`
    - `OPENROUTER_API_KEY`, `OPENROUTER_API_BASE_URL` (optional OCR/ASR)
    - `SECRET_KEY` (JWT signing), `MEDICAL_DATA_KEY` (Fernet encryption)
  - Observability:
    - `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`, `OTEL_SERVICE_NAME`
  - Frontend:
    - `VITE_API_BASE_URL` pointing to Gateway (dev: `http://localhost:8000`)
- Installation (local dev):
  - Frontend:
    - `cd frontend && npm install && npm --workspace packages/app run dev`
  - Backend services (uv workspaces):
    - `cd backend/app && make install`
    - `make run-gateway` (port 8000)
    - `make run-user` (port 8001)
    - `make run-chat` (port 8003)
    - `make run-ai` (port 8004)
  - Local stack (recommended):
    - `docker compose -f infra/local/docker-compose.yml up -d`


## 3. Usage Guide
- Running the Application:
  - Gateway API: `http://localhost:8000`
  - Frontend (dev): `http://localhost:5173` (reads `VITE_API_BASE_URL`)
  - Services: `user` 8001, `chat` 8003, `ai` 8004
- Common Commands:
  - Ingest document via service: `python backend/scripts/ingest_documents.py <filepath> --user-id 0 --mode http`
  - Check service health: `GET /ping` on each service
  - Fetch conversation graph: `GET /api/v1/graph/{conv_id}`
- Example Flows:
  - Chat:
    - `POST /api/v1/chat/query` with `{ text }` → answer + `conv_id` (chat routing: `backend/app/services/chat_service/chat_service/api/v1/chat.py:22`)
  - Voice:
    - Upload audio to `POST /api/v1/voice` (frontend orchestration: `frontend/packages/chat/src/components/Chat.jsx:69`)
  - OCR:
    - Upload image to `POST /api/v1/ocr` (frontend orchestration: `frontend/packages/chat/src/components/Chat.jsx:92`)
  - Indexing:
    - `POST /api/v1/index` with `{ user_id, text, metadata }` (AI service: `backend/app/services/ai_service/ai_service/main.py:101`)
  - Embeddings:
    - `POST /api/v1/embed` with `{ text }` → `{ vector, dim }` (AI service: `backend/app/services/ai_service/ai_service/main.py:104`)


## 4. Architecture Documentation
- System Diagram (Mermaid):
```
flowchart LR
  Browser[Frontend (React/Vite)] -->|/auth/*, /api/v1/*| GW[Gateway]
  GW --> US[User Service]
  GW --> CS[Chat Service]
  GW --> AI[AI Service]
  CS -->|persist| MG[MongoDB]
  CS -->|search| QD[Qdrant]
  AI -->|generate| OL[Ollama (GPU)]
  AI -->|OCR/ASR| OR[OpenRouter]
  subgraph Observability
    GF[Grafana] --- PM[Prometheus]
    PM --- TP[Tempo]
    PM --- LK[Loki]
  end
  GW --- TP
  US --- TP
  CS --- TP
  AI --- TP
```
- Data Flow (Mermaid sequence):
```
sequenceDiagram
  participant UI as Frontend
  participant GW as Gateway
  participant US as User
  participant CS as Chat
  participant AI as AI
  participant DB as Mongo
  participant VDB as Qdrant

  UI->>GW: /auth/login
  GW->>US: Proxy
  US-->>GW: token + user
  GW-->>UI: token + user

  UI->>GW: /api/v1/chat/query { text }
  GW->>CS: Proxy
  CS->>VDB: Similarity search
  CS->>AI: Generate with context
  AI-->>CS: Answer
  CS->>DB: Persist conversation + graph
  CS-->>GW: { answer, conv_id }
  GW-->>UI: { answer, conv_id }
```
- Important Design Decisions:
  - Microservices separation for authentication, chat orchestration, and AI generation improves scalability and compliance boundaries.
  - Retrieval‑Augmented Generation using Qdrant enables context grounding from ingested medical documents.
  - Observability is first‑class via OpenTelemetry exporters in each service (`backend/app/shared/logger.py:5`).
  - Sensitive data encrypted with Fernet before persistence (`backend/app/services/ai_service/ai_service/security.py:15`).
  - Gateway acts as the single external ingress with consistent CORS/security (`backend/app/gateway/gateway/main.py:33`).


## 5. Development Guidelines
- Contribution Process:
  - Fork and branch per feature; submit PRs with clear scope and linked issues.
  - Keep changes small and focused; include tests and updates to docs.
- Coding Standards:
  - Python: type hints, Pydantic models for payloads, idiomatic FastAPI routes.
  - Frontend: Redux Toolkit for state, components under `shared`, consistent Tailwind classes.
  - Security: JWT for auth (`backend/app/services/user_service/user_service/api/auth.py:82`), least privilege DB access.
- Testing Approach:
  - Backend: add `pytest` suites per service; existing chat API tests (`backend/app/services/chat_service/tests/test_chat_api.py`).
  - Frontend: Jest + React Testing Library; unit test slices and components.
- Deployment Procedures:
  - Local: `infra/local/docker-compose.yml` for services + observability.
  - k3s/Helm: `infra/K3s/charts/genai` chart; configure ingress hosts, TLS, replicas, and resources.
  - HPAs enabled for gateway/chat/ai (`infra/K3s/charts/genai/templates/hpa.yaml:1`).
  - Secrets managed via Kubernetes Secrets (`infra/K3s/charts/genai/templates/secrets.yaml`).
  - See `infra/Development_Guide.md` for detailed developer workflows.


## 6. API Reference (Selected)
- Gateway: proxies `/auth/*`, `/api/v1/*` (gateway proxy: `backend/app/gateway/gateway/main.py:33`)
- User Service:
  - `POST /auth/register`, `POST /auth/login`, `GET /auth/me` (`backend/app/services/user_service/user_service/api/auth.py:46`)
- Chat Service:
  - `POST /api/v1/chat/query` (`backend/app/services/chat_service/chat_service/api/v1/chat.py:22`)
  - `POST /api/v1/ingest/upload` (`backend/app/services/chat_service/chat_service/api/v1/ingest.py:12`)
  - `GET /api/v1/graph/{conv_id}` (`backend/app/services/chat_service/chat_service/api/v1/graph.py:8`)
- AI Service:
  - `POST /api/v1/generate` (`backend/app/services/ai_service/ai_service/main.py:36`)
  - `POST /api/v1/ocr`, `POST /api/v1/voice` (`backend/app/services/ai_service/ai_service/main.py:70`, `:85`)
  - `POST /api/v1/index` (secure ingest: `backend/app/services/ai_service/ai_service/main.py:101`)
  - `POST /api/v1/embed` (embeddings: `backend/app/services/ai_service/ai_service/main.py:104`)


## 7. Infrastructure & Sizing
- Minimum Recommended (excluding Ollama GPU node):
  - 6 vCPU, 12 GB RAM, 100 GB NVMe (or 200 GB SSD)
  - Breakdown: Backend 3 vCPU/6 GB, Frontend 1 vCPU/2 GB, Qdrant 1 vCPU/2 GB, Grafana stack ~1 vCPU/2 GB, reserve ~10% for k3s overhead.
- Storage:
  - NVMe preferred for Qdrant; minimum 100 GB for app data, logs, metrics, and k8s system.
- Scaling:
  - Vertical first (increase limits/requests), then horizontal (replicas + HPAs).
  - High traffic target: 8 vCPU, 16 GB RAM, 200 GB NVMe.
  - Helm resources tuned in templates (gateway/chat/ai/user/qdrant/frontend/observability). Adjust in `values.yaml` per environment.


## 8. Troubleshooting & Observability
- Tracing: OTLP to Tempo; view service graphs and spans in Grafana.
- Metrics: Prometheus scrape; set alerts on p95 latency and error rate.
- Logs: Loki + Promtail; correlate by `service.name`.
- Scripts: `infra/scripts/collect_logs.sh` for quick log retrieval (Grafana/Tempo/Prometheus configured in chart).


## 9. License and Contact
- License: Proprietary or organizational license (update as applicable).
- Contact: Platform engineering team; SRE for operations; security for keys/secrets.

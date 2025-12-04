#!/usr/bin/env bash
set -euo pipefail

NS="genai"
kubectl -n "$NS" logs deploy/gateway --since 1h > gateway.log || true
kubectl -n "$NS" logs deploy/chat-service --since 1h > chat_service.log || true
kubectl -n "$NS" logs deploy/ai-service --since 1h > ai_service.log || true
kubectl -n "$NS" logs deploy/user-service --since 1h > user_service.log || true
kubectl -n "$NS" logs deploy/worker --since 1h > worker.log || true
kubectl -n "$NS" logs deploy/frontend --since 1h > frontend.log || true

#!/usr/bin/env bash
set -euo pipefail

docker logs genai_gateway --since 1h > gateway.log || true
docker logs genai_chat_service --since 1h > chat_service.log || true
docker logs genai_ai_service --since 1h > ai_service.log || true
docker logs genai_user_service --since 1h > user_service.log || true

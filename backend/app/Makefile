PYTHON=python3

.PHONY: install run-gateway run-user run-product run-chat run-ai

install:
	@echo "Syncing dependencies with uv for shared, gateway, user_service, product_service, chat_service"
	uv sync --package shared
	uv sync --package gateway
	uv sync --package user_service
	uv sync --package product_service
	uv sync --package chat_service
	uv sync --package ai_service

run-gateway:
	uv run --package gateway uvicorn gateway.main:app --reload --port 8000

run-user:
	uv run --package user_service uvicorn user_service.main:app --reload --port 8001

run-product:
	uv run --package product_service uvicorn product_service.main:app --reload --port 8002

run-chat:
	uv run --package chat_service uvicorn chat_service.main:app --reload --port 8003

run-ai:
	uv run --package ai_service uvicorn ai_service.main:app --reload --port 8004
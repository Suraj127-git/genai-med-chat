PYTHON=python3

.PHONY: install run-gateway run-user run-product

install:
	@echo "Installing shared, gateway, user_service, product_service"
	@(cd shared && poetry install)
	@(cd gateway && poetry install)
	@(cd services/user_service && poetry install)
	@(cd services/product_service && poetry install)
	@(cd services/chat_service && poetry install)

run-gateway:
	@(cd gateway && poetry run uvicorn gateway.main:app --reload --port 8000)

run-user:
	@(cd services/user_service && poetry run uvicorn user_service.main:app --reload --port 8001)

run-product:
	@(cd services/product_service && poetry run uvicorn product_service.main:app --reload --port 8002)

run-chat:
	@(cd services/chat_service && poetry run uvicorn chat_service.main:app --reload --port 8003)
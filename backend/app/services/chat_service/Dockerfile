FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy shared lib and chat_service code
COPY backend/shared/shared /app/shared
COPY backend/app/services/chat_service /app/chat_service

RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy pymysql requests pydantic-settings

ENV PYTHONPATH=/app
EXPOSE 8003

CMD ["uvicorn", "chat_service.main:app", "--host", "0.0.0.0", "--port", "8003"]

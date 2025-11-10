FROM python:3.12-slim

# Minimal system deps for MySQL client builds
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy shared lib and chat_service code
COPY ../../shared/shared /app/shared
COPY ./chat_service /app/chat_service

# Install required Python deps (keep image light; optional libs are omitted)
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy pymysql requests pydantic-settings

ENV PYTHONPATH=/app
EXPOSE 8003

CMD ["uvicorn", "chat_service.main:app", "--host", "0.0.0.0", "--port", "8003"]
# backend/app/services/chat_service/Dockerfile
FROM python:3.12-slim

# Install system deps needed for building some Python packages (MySQL client etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# =========================
# Install Python deps from requirements (exported by Poetry)
# =========================
# Expect a requirements.txt at backend/app/services/chat_service/requirements.txt
COPY ./backend/app/services/chat_service/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r /tmp/requirements.txt

# =========================
# Copy project source and shared library
# =========================
# According to your repo tree, code lives under:
# backend/app/services/chat_service/chat_service
# backend/app/shared/shared
COPY ./backend/app/shared/shared /app/shared
COPY ./backend/app/services/chat_service/chat_service /app/chat_service

ENV PYTHONPATH=/app
EXPOSE 8003

# Run the service
CMD ["uvicorn", "chat_service.main:app", "--host", "0.0.0.0", "--port", "8003"]

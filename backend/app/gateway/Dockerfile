FROM python:3.12-slim

WORKDIR /app

# Copy shared lib and gateway code
COPY backend/shared/shared /app/shared
COPY backend/app/gateway /app/gateway

RUN pip install --no-cache-dir fastapi uvicorn httpx

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]

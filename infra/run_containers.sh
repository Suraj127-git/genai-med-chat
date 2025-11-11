#!/bin/bash

# Exit on any error
set -e

# -----------------------------
# Variables
# -----------------------------
BACKEND_DIR="../backend"
FRONTEND_DIR="../frontend"

BACKEND_IMAGE="infra-backend"
CELERY_IMAGE="infra-celery"
FRONTEND_IMAGE="infra-frontend"

NETWORK_NAME="infra-network"

# -----------------------------
# Step 1: Create Docker network
# -----------------------------
docker network inspect $NETWORK_NAME >/dev/null 2>&1 || \
docker network create $NETWORK_NAME
echo "✅ Network '$NETWORK_NAME' is ready."

# -----------------------------
# Step 2: Build images
# -----------------------------
echo "🔧 Building backend image..."
docker build -t $BACKEND_IMAGE $BACKEND_DIR

echo "🔧 Building celery image..."
docker build -t $CELERY_IMAGE $BACKEND_DIR

echo "🔧 Building frontend image..."
docker build -t $FRONTEND_IMAGE $FRONTEND_DIR

# -----------------------------
# Step 3: Run containers
# -----------------------------

# ✅ MySQL
docker run -d \
  --name infra-mysql \
  --network $NETWORK_NAME \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=genai_med \
  -e MYSQL_USER=genai \
  -e MYSQL_PASSWORD=genai \
  -p 3306:3306 \
  -v ../data/mysql:/var/lib/mysql \
  --restart always \
  mysql:8.0
echo "✅ MySQL container started."

# ✅ Redis
docker run -d \
  --name infra-redis \
  --network $NETWORK_NAME \
  -p 6379:6379 \
  -v ../data/redis:/data \
  --restart always \
  redis:7.2
echo "✅ Redis container started."

# ✅ Qdrant
docker run -d \
  --name infra-qdrant \
  --network $NETWORK_NAME \
  -p 6333:6333 -p 6334:6334 \
  -v ../data/qdrant:/qdrant/storage \
  --restart always \
  qdrant/qdrant:v1.10.0
echo "✅ Qdrant container started."

# ✅ Backend
docker run -d \
  --name infra-backend \
  --network $NETWORK_NAME \
  -p 8000:8000 \
  -v $BACKEND_DIR:/app \
  -e DATABASE_URL=mysql+pymysql://genai:genai@infra-mysql:3306/genai_med \
  -e REDIS_URL=redis://infra-redis:6379 \
  -e QDRANT_URL=http://infra-qdrant:6333 \
  --restart always \
  $BACKEND_IMAGE \
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo "✅ Backend container started."

# ✅ Celery
docker run -d \
  --name infra-celery \
  --network $NETWORK_NAME \
  -v $BACKEND_DIR:/app \
  -e DATABASE_URL=mysql+pymysql://genai:genai@infra-mysql:3306/genai_med \
  -e REDIS_URL=redis://infra-redis:6379 \
  -e QDRANT_URL=http://infra-qdrant:6333 \
  --restart always \
  $CELERY_IMAGE \
  celery -A app.tasks.celery_app worker --loglevel=info
echo "✅ Celery container started."

# ✅ Frontend
docker run -d \
  --name infra-frontend \
  --network $NETWORK_NAME \
  -p 3000:3000 \
  -v $FRONTEND_DIR:/app \
  --restart always \
  $FRONTEND_IMAGE \
  npm run dev
echo "✅ Frontend container started."

echo ""
echo "🚀 All containers are up and running successfully!"

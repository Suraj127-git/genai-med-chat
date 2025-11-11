#!/bin/bash
set -e

echo "📦 Building and starting infrastructure..."
docker compose down -v
docker compose build
docker compose up -d

echo "⏳ Waiting for MySQL to be healthy..."
until [ "$(docker inspect -f '{{.State.Health.Status}}' $(docker ps -qf name=mysql))" == "healthy" ]; do
  echo "MySQL is not ready yet..."
  sleep 3
done

echo "✅ All services are up!"
docker compose ps

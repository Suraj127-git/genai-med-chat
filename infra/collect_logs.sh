#!/bin/bash

# Collect logs from all containers defined in infra/docker-compose.yml
# Writes files named after each container (e.g., genai_chat_service.txt)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

# Output directory can be provided as first argument; defaults to infra/logs
OUT_DIR="${1:-$SCRIPT_DIR/logs}"
mkdir -p "$OUT_DIR"

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "docker-compose.yml not found at $COMPOSE_FILE" >&2
  exit 1
fi

# Extract container names from compose file (services use container_name: ...)
mapfile -t CONTAINERS < <(grep -E "^\s*container_name:\s*" "$COMPOSE_FILE" | sed -E 's/^\s*container_name:\s*//' | tr -d '\r')

if [ ${#CONTAINERS[@]} -eq 0 ]; then
  echo "No container_name entries found in compose file." >&2
  exit 1
fi

echo "Found containers: ${CONTAINERS[*]}"

# Collect logs for each container
for c in "${CONTAINERS[@]}"; do
  LOG_FILE="$OUT_DIR/${c}.txt"
  echo "Collecting logs for $c -> $LOG_FILE"
  if docker inspect "$c" >/dev/null 2>&1; then
    # Capture logs; include timestamps; don't fail the whole script on errors
    docker logs --timestamps "$c" >"$LOG_FILE" 2>&1 || echo "Failed to get logs for $c" >>"$LOG_FILE"
  else
    echo "Container $c not found or not running." >"$LOG_FILE"
  fi
done

echo "Logs saved to $OUT_DIR"
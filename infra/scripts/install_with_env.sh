#!/usr/bin/env bash
set -euo pipefail

RELEASE_NAME="genai"
NAMESPACE="genai"

while getopts ":r:n:" opt; do
  case $opt in
    r) RELEASE_NAME="$OPTARG" ;;
    n) NAMESPACE="$OPTARG" ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_INFRA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$REPO_INFRA_DIR/env/.env"
CHART_PATH="$REPO_INFRA_DIR/k8s/charts/genai"

if ! command -v helm >/dev/null 2>&1; then echo "helm not found"; exit 1; fi
if [ ! -f "$ENV_FILE" ]; then echo "env file not found: $ENV_FILE"; exit 1; fi

declare -A MAP
MAP[OPENROUTER_API_KEY]=secrets.OPENROUTER_API_KEY
MAP[SECRET_KEY]=secrets.SECRET_KEY
MAP[LANGSMITH_API_KEY]=secrets.LANGSMITH_API_KEY
MAP[LANGSMITH_TRACING]=config.LANGSMITH_TRACING
MAP[LANGSMITH_ENDPOINT]=config.LANGSMITH_ENDPOINT
MAP[LANGSMITH_PROJECT]=config.LANGSMITH_PROJECT

SET_ARGS=()
while IFS='=' read -r K V; do
  [ -z "${K}" ] && continue
  [[ "$K" =~ ^# ]] && continue
  V=${V%$'\r'}
  if [ -n "${MAP[$K]:-}" ] && [ -n "$V" ]; then
    SET_ARGS+=("--set-string" "${MAP[$K]}=$V")
  fi
done < "$ENV_FILE"

helm upgrade --install "$RELEASE_NAME" "$CHART_PATH" -n "$NAMESPACE" --create-namespace -f "$CHART_PATH/values-k3s.yaml" "${SET_ARGS[@]}" ${EXTRA_SET_ARGS:-}

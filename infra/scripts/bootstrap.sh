#!/usr/bin/env bash
set -euo pipefail

RELEASE_NAME="genai"
NAMESPACE="genai"
TLS_CERT_PATH=""
TLS_KEY_PATH=""
INGRESS_URL=""
FRONTEND_IMAGE="shettyanna/genai-frontend:latest"
VITE_API_BASE_URL="http://gateway:8000"
BUILD_FRONTEND="false"

while getopts ":r:n:c:k:i:f:a:b:" opt; do
  case $opt in
    r) RELEASE_NAME="$OPTARG" ;;
    n) NAMESPACE="$OPTARG" ;;
    c) TLS_CERT_PATH="$OPTARG" ;;
    k) TLS_KEY_PATH="$OPTARG" ;;
    i) INGRESS_URL="$OPTARG" ;;
    f) FRONTEND_IMAGE="$OPTARG" ;;
    a) VITE_API_BASE_URL="$OPTARG" ;;
    b) BUILD_FRONTEND="$OPTARG" ;;
  esac
done

if ! command -v kubectl >/dev/null 2>&1; then echo "kubectl not found"; exit 1; fi
if ! command -v helm >/dev/null 2>&1; then echo "helm not found"; exit 1; fi

VITE_API_BASE_URL="${VITE_API_BASE_URL//\`/}"

if ! kubectl cluster-info >/dev/null 2>&1; then
  "$(dirname "$0")/kind_bootstrap.sh" -r "$RELEASE_NAME" -n "$NAMESPACE" -c "$TLS_CERT_PATH" -k "$TLS_KEY_PATH" -b "$BUILD_FRONTEND" -a "$VITE_API_BASE_URL" -f "$FRONTEND_IMAGE"
  exit 0
fi

kubectl get ns "$NAMESPACE" >/dev/null 2>&1 || kubectl create namespace "$NAMESPACE"
kubectl label namespace "$NAMESPACE" app.kubernetes.io/managed-by=Helm --overwrite || true
kubectl annotate namespace "$NAMESPACE" meta.helm.sh/release-name="$RELEASE_NAME" --overwrite || true
kubectl annotate namespace "$NAMESPACE" meta.helm.sh/release-namespace="$NAMESPACE" --overwrite || true

kubectl -n kube-system wait --for=condition=available deploy/traefik --timeout=300s || true

if [ -n "$TLS_CERT_PATH" ] && [ -n "$TLS_KEY_PATH" ]; then
  kubectl -n "$NAMESPACE" delete secret genai-tls --ignore-not-found
  kubectl -n "$NAMESPACE" create secret tls genai-tls --cert "$TLS_CERT_PATH" --key "$TLS_KEY_PATH"
else
  if ! command -v openssl >/dev/null 2>&1; then echo "openssl not found"; exit 1; fi
  TMPCRT="$(pwd)/tls.crt"; TMPKEY="$(pwd)/tls.key"
  [ -f "$TMPCRT" ] && [ -f "$TMPKEY" ] || openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "$TMPKEY" -out "$TMPCRT" -subj "/CN=*.genai.local"
  kubectl -n "$NAMESPACE" delete secret genai-tls --ignore-not-found
  kubectl -n "$NAMESPACE" create secret tls genai-tls --cert "$TMPCRT" --key "$TMPKEY"
fi

IP="$(kubectl -n kube-system get svc traefik -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)"
[ -z "$IP" ] && IP="$(kubectl -n kube-system get svc traefik -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)"
[ -z "$IP" ] && IP="$(kubectl -n kube-system get svc traefik -o jsonpath='{.spec.clusterIP}' 2>/dev/null || true)"
if [ -n "$IP" ]; then
  for H in api.genai.local app.genai.local grafana.genai.local prometheus.genai.local tempo.genai.local; do
    grep -qE "\s$H$" /etc/hosts || echo "$IP $H" | sudo tee -a /etc/hosts >/dev/null
  done
fi

if [ "$BUILD_FRONTEND" = "true" ]; then
  PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
  docker build -f "$PROJECT_ROOT/frontend/Dockerfile" --build-arg "VITE_API_BASE_URL=$VITE_API_BASE_URL" -t "$FRONTEND_IMAGE" "$PROJECT_ROOT/frontend"
  if [[ "$CTX" == kind* ]]; then
    kind load docker-image "$FRONTEND_IMAGE" --name "$RELEASE_NAME" || true
  else
    docker push "$FRONTEND_IMAGE" || true
  fi
fi

"$(dirname "$0")/install_with_env.sh" -r "$RELEASE_NAME" -n "$NAMESPACE"

kubectl -n "$NAMESPACE" get all
kubectl -n "$NAMESPACE" wait --for=condition=available deploy --all --timeout=600s || true

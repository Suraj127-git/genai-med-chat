#!/usr/bin/env bash
set -euo pipefail

RELEASE_NAME="genai"
NAMESPACE="genai"
TLS_CERT_PATH=""
TLS_KEY_PATH=""
FRONTEND_IMAGE="shettyanna/genai-frontend:latest"
VITE_API_BASE_URL="http://gateway:8000"
BUILD_FRONTEND="false"

while getopts ":r:n:c:k:f:a:b:" opt; do
  case $opt in
    r) RELEASE_NAME="$OPTARG" ;;
    n) NAMESPACE="$OPTARG" ;;
    c) TLS_CERT_PATH="$OPTARG" ;;
    k) TLS_KEY_PATH="$OPTARG" ;;
    f) FRONTEND_IMAGE="$OPTARG" ;;
    a) VITE_API_BASE_URL="$OPTARG" ;;
    b) BUILD_FRONTEND="$OPTARG" ;;
  esac
done

command -v kubectl >/dev/null 2>&1 || { echo "kubectl not found"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "helm not found"; exit 1; }

if ! command -v k3s >/dev/null 2>&1; then
  curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
fi

kubectl wait --for=condition=Ready node --all --timeout=300s || true
kubectl -n kube-system wait --for=condition=available deploy/traefik --timeout=300s || true

SVC_IP="$(kubectl -n kube-system get svc traefik -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)"
[ -z "$SVC_IP" ] && SVC_IP="$(kubectl -n kube-system get svc traefik -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)"
[ -z "$SVC_IP" ] && SVC_IP="$(kubectl -n kube-system get svc traefik -o jsonpath='{.spec.clusterIP}' 2>/dev/null || true)"

for H in api.genai.local app.genai.local grafana.genai.local prometheus.genai.local tempo.genai.local; do
  if [ -n "$SVC_IP" ]; then
    grep -qE "\s$H$" /etc/hosts || echo "$SVC_IP $H" | sudo tee -a /etc/hosts >/dev/null
  fi
done

kubectl get ns "$NAMESPACE" >/dev/null 2>&1 || kubectl create namespace "$NAMESPACE"
kubectl label namespace "$NAMESPACE" app.kubernetes.io/managed-by=Helm --overwrite || true
kubectl annotate namespace "$NAMESPACE" meta.helm.sh/release-name="$RELEASE_NAME" --overwrite || true
kubectl annotate namespace "$NAMESPACE" meta.helm.sh/release-namespace="$NAMESPACE" --overwrite || true

if [ -n "$TLS_CERT_PATH" ] && [ -n "$TLS_KEY_PATH" ]; then
  kubectl -n "$NAMESPACE" delete secret genai-tls --ignore-not-found
  kubectl -n "$NAMESPACE" create secret tls genai-tls --cert "$TLS_CERT_PATH" --key "$TLS_KEY_PATH"
fi

if [ "$BUILD_FRONTEND" = "true" ]; then
  PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
  docker build -f "$PROJECT_ROOT/frontend/Dockerfile" --build-arg "VITE_API_BASE_URL=$VITE_API_BASE_URL" -t "$FRONTEND_IMAGE" "$PROJECT_ROOT/frontend"
  docker push "$FRONTEND_IMAGE" || true
fi

"$(dirname "$0")/install_with_env.sh" -r "$RELEASE_NAME" -n "$NAMESPACE"

kubectl -n "$NAMESPACE" get all
kubectl -n "$NAMESPACE" wait --for=condition=available deploy --all --timeout=600s || true

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

if ! command -v kind >/dev/null 2>&1; then
  curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.23.0/kind-linux-amd64
  chmod +x kind
  sudo mv kind /usr/local/bin/kind
fi

docker pull kindest/node:v1.34.0 || true

if ! docker info >/dev/null 2>&1; then
  if command -v systemctl >/dev/null 2>&1; then sudo systemctl start docker || true; fi
fi

if ! kubectl config get-contexts | grep -q "kind-$RELEASE_NAME"; then
  for attempt in 1 2 3; do
    kind create cluster --name "$RELEASE_NAME" --image kindest/node:v1.34.0 --wait 180s && break
    sleep 5
  done
fi

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx wait --for=condition=available deploy/ingress-nginx-controller --timeout=300s || true

kubectl wait --for=condition=Ready node --all --timeout=180s || true

for H in api.genai.local app.genai.local grafana.genai.local prometheus.genai.local tempo.genai.local; do
  grep -qE "\s$H$" /etc/hosts || echo "127.0.0.1 $H" | sudo tee -a /etc/hosts >/dev/null
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
  kind load docker-image "$FRONTEND_IMAGE" --name "$RELEASE_NAME" || true
fi

export EXTRA_SET_ARGS="--set imagePullPolicy=IfNotPresent"
"$(dirname "$0")/install_with_env.sh" -r "$RELEASE_NAME" -n "$NAMESPACE"

kubectl -n "$NAMESPACE" get all
kubectl -n "$NAMESPACE" wait --for=condition=available deploy --all --timeout=600s || true

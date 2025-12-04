#!/usr/bin/env bash
set -euo pipefail
INGRESS_NAMESPACE="kube-system"
APP_NAMESPACE="genai"
TLS_CERT_PATH=""
TLS_KEY_PATH=""
HOSTS=("api.genai.local" "app.genai.local" "grafana.genai.local" "prometheus.genai.local" "tempo.genai.local")
while getopts ":i:a:c:k:" opt; do
  case $opt in
    i) INGRESS_NAMESPACE="$OPTARG" ;;
    a) APP_NAMESPACE="$OPTARG" ;;
    c) TLS_CERT_PATH="$OPTARG" ;;
    k) TLS_KEY_PATH="$OPTARG" ;;
  esac
done
command -v kubectl >/dev/null 2>&1 || { echo "kubectl not found"; exit 1; }
kubectl -n "$INGRESS_NAMESPACE" wait --for=condition=available deploy/traefik --timeout=300s || true
IP="$(kubectl -n "$INGRESS_NAMESPACE" get svc traefik -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || true)"
[ -z "$IP" ] && IP="$(kubectl -n "$INGRESS_NAMESPACE" get svc traefik -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)"
[ -z "$IP" ] && IP="$(kubectl -n "$INGRESS_NAMESPACE" get svc traefik -o jsonpath='{.spec.clusterIP}' 2>/dev/null || true)"
if [ -n "$TLS_CERT_PATH" ] && [ -n "$TLS_KEY_PATH" ]; then
  kubectl -n "$APP_NAMESPACE" delete secret genai-tls --ignore-not-found
  kubectl -n "$APP_NAMESPACE" create secret tls genai-tls --cert "$TLS_CERT_PATH" --key "$TLS_KEY_PATH"
fi
for H in "${HOSTS[@]}"; do
  if [ -n "$IP" ] && ! grep -qE "\s$H$" /etc/hosts; then
    echo "$IP $H" | sudo tee -a /etc/hosts >/dev/null || true
  fi
done
kubectl -n "$APP_NAMESPACE" get svc || true
kubectl -n "$APP_NAMESPACE" get ingress || true

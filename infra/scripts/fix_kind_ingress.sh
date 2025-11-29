#!/usr/bin/env bash
set -euo pipefail
INGRESS_NAMESPACE="ingress-nginx"
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
if kubectl get ns "$INGRESS_NAMESPACE" >/dev/null 2>&1; then
  kubectl -n "$INGRESS_NAMESPACE" delete deploy ingress-nginx-controller --ignore-not-found || true
  kubectl -n "$INGRESS_NAMESPACE" delete svc ingress-nginx-controller --ignore-not-found || true
fi
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl -n "$INGRESS_NAMESPACE" wait --for=condition=available deploy/ingress-nginx-controller --timeout=300s
HP="$(kubectl -n "$INGRESS_NAMESPACE" get deploy ingress-nginx-controller -o jsonpath='{range .spec.template.spec.containers[0].ports[*]}{.hostPort}{"\n"}{end}' || true)"
echo "$HP" | grep -q "^80$" || { echo "hostPort 80 not configured"; exit 1; }
echo "$HP" | grep -q "^443$" || { echo "hostPort 443 not configured"; exit 1; }
if [ -n "$TLS_CERT_PATH" ] && [ -n "$TLS_KEY_PATH" ]; then
  kubectl -n "$APP_NAMESPACE" delete secret genai-tls --ignore-not-found
  kubectl -n "$APP_NAMESPACE" create secret tls genai-tls --cert "$TLS_CERT_PATH" --key "$TLS_KEY_PATH"
fi
for H in "${HOSTS[@]}"; do
  if ! grep -qE "\s$H$" /etc/hosts; then
    echo "127.0.0.1 $H" | sudo tee -a /etc/hosts >/dev/null || true
  fi
done
kubectl -n "$APP_NAMESPACE" get svc frontend || true
kubectl -n "$APP_NAMESPACE" get ingress || true

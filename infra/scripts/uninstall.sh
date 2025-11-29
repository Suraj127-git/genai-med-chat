#!/usr/bin/env bash
set -euo pipefail

RELEASE_NAME="genai"
NAMESPACE="genai"
DELETE_NS="false"

while getopts ":r:n:d:" opt; do
  case $opt in
    r) RELEASE_NAME="$OPTARG" ;;
    n) NAMESPACE="$OPTARG" ;;
    d) DELETE_NS="$OPTARG" ;;
  esac
done

helm uninstall "$RELEASE_NAME" -n "$NAMESPACE" || true
if [ "$DELETE_NS" = "true" ]; then kubectl delete namespace "$NAMESPACE" || true; fi

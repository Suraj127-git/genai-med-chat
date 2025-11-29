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

"$(dirname "$0")/install_with_env.sh" -r "$RELEASE_NAME" -n "$NAMESPACE"

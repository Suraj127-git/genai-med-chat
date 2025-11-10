#!/usr/bin/env bash
set -euo pipefail

# Clean script for the frontend monorepo
# Removes node_modules and dist folders in root and all packages

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Cleaning frontend workspace at: $ROOT_DIR"

# Remove root node_modules if present
if [ -d "$ROOT_DIR/node_modules" ]; then
  echo "Removing: $ROOT_DIR/node_modules"
  rm -rf "$ROOT_DIR/node_modules"
fi

# Iterate packages and remove node_modules and dist
PACKAGES_DIR="$ROOT_DIR/packages"
if [ -d "$PACKAGES_DIR" ]; then
  for pkg in "$PACKAGES_DIR"/*; do
    [ -d "$pkg" ] || continue

    if [ -d "$pkg/node_modules" ]; then
      echo "Removing: $pkg/node_modules"
      rm -rf "$pkg/node_modules"
    fi

    if [ -d "$pkg/dist" ]; then
      echo "Removing: $pkg/dist"
      rm -rf "$pkg/dist"
    fi
  done
fi

echo "Clean complete."
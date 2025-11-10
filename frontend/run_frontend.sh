#!/bin/bash

# Exit immediately on error
set -e

# Go to the script's directory
cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build all packages using local Lerna
echo "🏗️ Building all packages..."
npx lerna run build


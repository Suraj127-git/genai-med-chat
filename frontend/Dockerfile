# syntax=docker/dockerfile:1

# ------------------------------------------------------------
# Dependencies stage: install monorepo deps with caching
# ------------------------------------------------------------
FROM node:20-alpine AS deps
WORKDIR /app

# Copy root manifests (workspace root inside the frontend context)
# Make sure you build with context = ./frontend
COPY package.json package-lock.json lerna.json ./

# Copy workspace package manifests to leverage layer caching
# This copies package.json for each package (packages/app, packages/*)
COPY packages/*/package.json packages/*/

# Install deps using lockfile (reproducible)
RUN npm ci --production=false

# ------------------------------------------------------------
# Development stage: run Vite dev server (default image)
# ------------------------------------------------------------
FROM node:20-alpine AS dev
WORKDIR /app
ENV NODE_ENV=development

# Copy source code from the frontend context
COPY . .

# Reuse node_modules installed in deps stage
COPY --from=deps /app/node_modules /app/node_modules

# Expose Vite dev port
EXPOSE 5173

# Default command for dev image
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ------------------------------------------------------------
# Build stage: produce production assets
# ------------------------------------------------------------
FROM node:20-alpine AS builder
WORKDIR /app
ENV NODE_ENV=production

# Copy source and installed dependencies
COPY . .
COPY --from=deps /app/node_modules /app/node_modules

# Pass-through build-time arg for Vite
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build all packages (assumes `frontend/package.json` has "build": "lerna run build")
# If your build script differs, adjust accordingly.
RUN npm run build

# ------------------------------------------------------------
# Production stage: serve static assets via NGINX
# ------------------------------------------------------------
FROM nginx:alpine AS prod

# Remove default nginx html and copy built SPA (packages/app/dist)
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/packages/app/dist /usr/share/nginx/html

# Optionally add nginx config to support client-side routing:
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

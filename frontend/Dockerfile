# syntax=docker/dockerfile:1

# ------------------------------------------------------------
# Dependencies stage: install monorepo deps with caching
# ------------------------------------------------------------
FROM node:20-alpine AS deps
WORKDIR /app

# Copy root manifests
COPY package.json package-lock.json lerna.json ./

# Copy workspace manifests to improve caching
COPY packages/*/package.json packages/*/

# Use npm install (not npm ci) for monorepos/workspaces
# npm ci breaks with workspace links during Docker builds
RUN npm install

# ------------------------------------------------------------
# Development stage
# ------------------------------------------------------------
FROM node:20-alpine AS dev
WORKDIR /app
ENV NODE_ENV=development

COPY . .
COPY --from=deps /app/node_modules /app/node_modules

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ------------------------------------------------------------
# Build stage
# ------------------------------------------------------------
FROM node:20-alpine AS builder
WORKDIR /app
ENV NODE_ENV=production

COPY . .
COPY --from=deps /app/node_modules /app/node_modules

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build only the app workspace to ensure package-local PostCSS/Tailwind config is used
RUN npm --workspace packages/app run build

# ------------------------------------------------------------
# Production stage
# ------------------------------------------------------------
FROM nginx:alpine AS prod
WORKDIR /usr/share/nginx/html

COPY --from=builder /app/packages/app/dist .

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

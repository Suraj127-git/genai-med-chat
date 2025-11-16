# ---------- Builder stage: produce wheels (keeps build deps out of final image) ----------
FROM python:3.12-slim AS builder

ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# install minimal build deps needed to build binary packages
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     build-essential \
     gcc \
     git \
     default-libmysqlclient-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy local shared package and chat_service source (only what we need to build wheels)
COPY backend/app/shared /app/shared
COPY backend/app/services/chat_service/requirements.txt /app/requirements.txt

# Create an isolated virtualenv (optional - but ensures pip builds use same python env)
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel

# Build wheels for all requirements into /wheels
RUN /opt/venv/bin/pip wheel --wheel-dir=/wheels -r /app/requirements.txt

# ---------- Runtime stage: minimal runtime with only the wheels installed ----------
FROM python:3.12-slim AS runtime

ARG DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install only runtime OS libs needed by binary wheels (not build tools)
# Keep list small; add libs if packages fail at runtime (e.g., libsm6 for OpenCV).
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
     ca-certificates \
     libgomp1 \
     libstdc++6 \
     default-libmysqlclient-dev \
  && rm -rf /var/lib/apt/lists/*

# Create venv in runtime and add it to PATH
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy pre-built wheels from builder and install them (no build tools needed)
COPY --from=builder /wheels /wheels
COPY backend/app/services/chat_service/requirements.txt /app/requirements.txt

# Copy source AFTER dependencies so changes in code don't bust wheel cache step
COPY backend/app/shared /app/shared
COPY backend/app/services/chat_service/chat_service /app/chat_service

# Install wheels from /wheels (fast and doesn't require compilers)
RUN pip install --upgrade pip \
    && pip install --no-index --find-links=/wheels -r /app/requirements.txt \
    && rm -rf /wheels /root/.cache/pip

# Set import path and port
ENV PYTHONPATH=/app
EXPOSE 8003

# Run uvicorn using package path chat_service.main
CMD ["uvicorn", "chat_service.main:app", "--host", "0.0.0.0", "--port", "8003"]

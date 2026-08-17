# syntax=docker/dockerfile:1

# ===== Frontend build stage (Next.js standalone) =====
FROM node:20-alpine AS web-builder
WORKDIR /build
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
# Build with the backend reachable inside the runtime container on :8000.
ARG API_TARGET=http://localhost:8000
ENV API_TARGET=$API_TARGET
RUN npm run build
# .next/standalone now holds a self-contained server (copy needed static+public).

# ===== Backend runtime stage (Python FastAPI) =====
FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# System deps (Node 20 for the Next standalone server, build tools for wheels).
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates gnupg build-essential \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Backend Python deps (pinned in requirements.txt).
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source.
COPY . ./
# Don't overwrite the frontend that will be added below.
RUN rm -rf web/node_modules web/.next

# Copy the built standalone server + static assets.
COPY --from=web-builder /build/.next/standalone ./web-standalone/
COPY --from=web-builder /build/.next/static ./web-standalone/.next/static
COPY --from=web-builder /build/public ./web-standalone/public

# Runtime: backend (uvicorn) on :8000, frontend standalone on :3000.
# The frontend's next.config rewrites /api -> http://localhost:8000, so one
# public port (3000) serves the whole app on a single domain.
EXPOSE 3000
ENV PORT=3000 HOSTNAME=0.0.0.0 API_TARGET=http://localhost:8000
COPY web/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

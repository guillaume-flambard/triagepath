#!/bin/sh
# triagepath monolith entrypoint: run FastAPI backend + Next.js standalone
# (which proxies /api to the backend) on one container / one domain.
# The proxy serves the domain on PORT (8000, the frontend); the backend listens
# on BACKEND_PORT (8001) and is only reachable from inside the container.
set -e

PORT="${PORT:-8000}"
BACKEND_PORT="${BACKEND_PORT:-8001}"
export PORT

uvicorn api:app --host 0.0.0.0 --port "$BACKEND_PORT" &
BACKEND_PID=$!

node web-standalone/server.js &
FRONTEND_PID=$!

trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true' INT TERM

wait $FRONTEND_PID
kill $BACKEND_PID 2>/dev/null || true

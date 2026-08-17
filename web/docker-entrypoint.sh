#!/bin/sh
# triagepath monolith entrypoint.
#   nginx   :8000  -> /api/*  -> uvicorn :8001  (streaming, buffering off)
#                    -> /       -> Next.js :3000 (standalone)
set -e

export PORT="${PORT:-3000}"
export BACKEND_PORT="${BACKEND_PORT:-8001}"
# Next.js standalone uses HOSTNAME as the bind address; force it to loopback so
# nginx (127.0.0.1:3000) can always reach it, overriding any container-set hostname.
export HOSTNAME="127.0.0.1"

# Backend (FastAPI).
uvicorn api:app --host 0.0.0.0 --port "$BACKEND_PORT" &
BACKEND_PID=$!

# Frontend (Next.js standalone).
node web-standalone/server.js &
FRONTEND_PID=$!

# nginx in the foreground; it is the public entrypoint on the exposed port.
nginx -g 'daemon off;' &
NGINX_PID=$!

trap 'kill $BACKEND_PID $FRONTEND_PID $NGINX_PID 2>/dev/null || true' INT TERM

wait -n 2>/dev/null || wait $NGINX_PID
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true

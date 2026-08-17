#!/bin/sh
# triagepath monolith entrypoint.
#   nginx   :8000  -> /api/*  -> uvicorn :8001  (streaming, buffering off)
#                    -> /       -> Next.js :3000 (standalone)
set -e

# Next.js standalone uses PORT + HOSTNAME as its bind address. Force both so
# it always listens on 127.0.0.1:3000 (reachable by nginx), overriding any
# PORT/HOSTNAME Coolify injects (e.g. PORT=8000 from the exposed port).
export PORT="3000"
export BACKEND_PORT="${BACKEND_PORT:-8001}"
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

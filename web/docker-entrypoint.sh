#!/bin/sh
# triagepath monolith entrypoint: run FastAPI backend (:8000) + Next.js
# standalone (:3000, proxies /api to :8000) on one container / one domain.
# POSIX sh: no bash-only features (dash on python:slim).
set -e

# Start the backend in the background.
uvicorn api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Run the frontend in the background too.
node web-standalone/server.js &
FRONTEND_PID=$!

# Forward signals to both so the container shuts down cleanly.
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true' INT TERM

# Wait for the frontend (primary). If it exits, tear down the backend too.
wait $FRONTEND_PID
kill $BACKEND_PID 2>/dev/null || true

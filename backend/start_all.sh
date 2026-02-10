#!/usr/bin/env bash
# Starts Redis, Celery worker, and FastAPI server together.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
    echo "Loaded environment from .env"
fi

set -e

cleanup() {
    echo "Shutting down..."
    kill -TERM "${CELERY_PIDS[@]}" $API_PID 2>/dev/null || true
    sleep 2
    kill -9 "${CELERY_PIDS[@]}" $API_PID 2>/dev/null || true
    redis-cli shutdown nosave 2>/dev/null || true
    wait 2>/dev/null || true
    echo "All processes stopped."
}

trap cleanup EXIT INT TERM

# 1. Start Redis
echo "Starting Redis..."
redis-server --daemonize yes --port 6379
sleep 1
echo "Redis running on :6379"

# 2. Start Celery workers (background, solo pool for CUDA compatibility)
NUM_WORKERS=${CELERY_WORKERS:-4}
echo "Starting $NUM_WORKERS Celery worker(s)..."
CELERY_PIDS=()
for i in $(seq 1 "$NUM_WORKERS"); do
    poetry run celery -A api.core.celery_app:celery_app worker \
        --loglevel=info \
        --pool=solo \
        -n "worker${i}@%h" &
    CELERY_PIDS+=($!)
    echo "Celery worker $i PID: $!"
done

# 3. Start FastAPI (foreground — Ctrl+C hits this, triggers cleanup)
echo "Starting FastAPI server..."
poetry run python -m api &
API_PID=$!
echo "FastAPI PID: $API_PID"

echo ""
echo "All services running. Press Ctrl+C to stop."
wait

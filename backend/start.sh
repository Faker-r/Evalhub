#!/bin/bash
set -e
echo "=== ENV DEBUG ==="
echo "DATABASE_URL set: $([ -n "$DATABASE_URL" ] && echo 'yes' || echo 'NO'), len=${#DATABASE_URL}, start=${DATABASE_URL:0:30}"
echo "JWT_SECRET set: $([ -n "$JWT_SECRET" ] && echo 'yes' || echo 'NO'), len=${#JWT_SECRET}"
echo "AWS_ACCESS_KEY_ID set: $([ -n "$AWS_ACCESS_KEY_ID" ] && echo 'yes' || echo 'NO'), len=${#AWS_ACCESS_KEY_ID}"
echo "AWS_SECRET_ACCESS_KEY set: $([ -n "$AWS_SECRET_ACCESS_KEY" ] && echo 'yes' || echo 'NO'), len=${#AWS_SECRET_ACCESS_KEY}"
echo "AWS_REGION=$AWS_REGION"
echo "S3_BUCKET_NAME=$S3_BUCKET_NAME"
echo "SUPABASE_URL set: $([ -n "$SUPABASE_URL" ] && echo 'yes' || echo 'NO'), start=${SUPABASE_URL:0:30}"
echo "SUPABASE_PUBLISHABLE_KEY set: $([ -n "$SUPABASE_PUBLISHABLE_KEY" ] && echo 'yes' || echo 'NO'), len=${#SUPABASE_PUBLISHABLE_KEY}"
echo "SUPABASE_SECRET_KEY set: $([ -n "$SUPABASE_SECRET_KEY" ] && echo 'yes' || echo 'NO'), len=${#SUPABASE_SECRET_KEY}"
echo "SUPABASE_JWT_SECRET set: $([ -n "$SUPABASE_JWT_SECRET" ] && echo 'yes' || echo 'NO'), len=${#SUPABASE_JWT_SECRET}"
echo "HF_TOKEN set: $([ -n "$HF_TOKEN" ] && echo 'yes' || echo 'NO'), len=${#HF_TOKEN}"
echo "REDIS_URL=$REDIS_URL"
echo "CELERY_WORKERS=$CELERY_WORKERS"
echo "=== END DEBUG ==="
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 1

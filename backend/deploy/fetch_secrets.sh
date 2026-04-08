#!/bin/bash
set -e

AWS_REGION="${AWS_REGION:-us-east-2}"
ENV_FILE="${ENV_FILE:-.env}"

KEYS=(
  DATABASE_URL
  JWT_SECRET
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  SUPABASE_URL
  SUPABASE_PUBLISHABLE_KEY
  SUPABASE_SECRET_KEY
  SUPABASE_JWT_SECRET
  HF_TOKEN
  REDIS_URL
)

tmp="${ENV_FILE}.tmp"
rm -f "$tmp"
for key in "${KEYS[@]}"; do
  val=$(aws secretsmanager get-secret-value \
    --secret-id "evalhub/$key" \
    --region "$AWS_REGION" \
    --query SecretString \
    --output text)
  printf '%s=%s\n' "$key" "$val" >> "$tmp"
done
mv "$tmp" "$ENV_FILE"
echo "Wrote $ENV_FILE"

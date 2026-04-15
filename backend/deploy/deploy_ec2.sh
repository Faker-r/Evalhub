#!/bin/bash
set -e

AWS_REGION="${AWS_REGION:-us-east-2}"
ECR_REGISTRY="${ECR_REGISTRY:-214863335048.dkr.ecr.us-east-2.amazonaws.com}"
ECR_REPOSITORY="${ECR_REPOSITORY:-evalhub-backend}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"

echo "=== EC2 Celery Deployment Script ==="
echo "Region: $AWS_REGION"
echo "Image: $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"

echo ""
echo "Step 1: Authenticating with ECR..."
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY"

echo ""
echo "Step 2: Pulling latest image..."
export ECR_IMAGE_URI="$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"
docker pull "$ECR_IMAGE_URI"

echo ""
echo "Step 3: Fetching secrets from AWS Secrets Manager..."
SECRET_NAMES=(
    "evalhub/DATABASE_URL"
    "evalhub/JWT_SECRET"
    "evalhub/AWS_ACCESS_KEY_ID"
    "evalhub/AWS_SECRET_ACCESS_KEY"
    "evalhub/SUPABASE_URL"
    "evalhub/SUPABASE_PUBLISHABLE_KEY"
    "evalhub/SUPABASE_SECRET_KEY"
    "evalhub/SUPABASE_JWT_SECRET"
    "evalhub/HF_TOKEN"
    "evalhub/REDIS_URL"
)

ENV_FILE=".env"
> "$ENV_FILE"

for secret_name in "${SECRET_NAMES[@]}"; do
    echo "Fetching $secret_name..."
    secret_value=$(aws secretsmanager get-secret-value \
        --region "$AWS_REGION" \
        --secret-id "$secret_name" \
        --query SecretString \
        --output text)
    
    env_key=$(echo "$secret_name" | sed 's/evalhub\///')
    echo "${env_key}=${secret_value}" >> "$ENV_FILE"
done

echo "AWS_REGION=$AWS_REGION" >> "$ENV_FILE"
echo "S3_BUCKET_NAME=evalhub-bucket" >> "$ENV_FILE"
echo "CELERY_WORKERS=4" >> "$ENV_FILE"

echo "Environment file created: $ENV_FILE"

echo ""
echo "Step 4: Stopping old containers..."
docker-compose -f "$COMPOSE_FILE" down || true

echo ""
echo "Step 5: Starting new Celery workers..."
docker-compose -f "$COMPOSE_FILE" up -d

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
bash "$SCRIPT_DIR/cleanup_ecr_repo_images.sh" "$ECR_IMAGE_URI"

echo ""
echo "Step 6: Waiting for workers to be ready..."
sleep 15

echo ""
echo "Step 7: Verifying worker health..."
docker-compose -f "$COMPOSE_FILE" ps

echo ""
echo "Step 8: Checking worker logs..."
docker-compose -f "$COMPOSE_FILE" logs --tail=20

echo ""
echo "=== Deployment Complete ==="
echo "Workers are running. Monitor with: docker-compose -f $COMPOSE_FILE logs -f"

#!/bin/bash
set -e

echo "=== Local Testing Script ==="
echo "This script tests the production Docker setup locally"

IMAGE_NAME="${IMAGE_NAME:-evalhub-backend-test}"
IMAGE_TAG="${IMAGE_TAG:-test}"

echo ""
echo "Step 1: Building Docker image..."
cd "$(dirname "$0")/.."
docker build -t "$IMAGE_NAME:$IMAGE_TAG" \
    --build-arg GIT_COMMIT="$(git rev-parse HEAD)" \
    --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --build-arg VERSION="test" \
    .

echo ""
echo "Step 2: Checking for .env file..."
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Please create one based on .env.example"
    exit 1
fi

echo ""
echo "Step 3: Starting services with docker-compose..."
export ECR_IMAGE_URI="$IMAGE_NAME:$IMAGE_TAG"
export CELERY_WORKERS=2

docker-compose -f docker-compose.yml up -d redis

sleep 5

docker-compose -f docker-compose.yml up -d api

echo ""
echo "Step 4: Waiting for API to be healthy..."
for i in {1..30}; do
    if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "API is healthy!"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "API health check timed out"
        docker-compose -f docker-compose.yml logs api
        exit 1
    fi
    echo "Waiting for API... ($i/30)"
    sleep 2
done

echo ""
echo "Step 5: Starting Celery worker..."
docker-compose -f docker-compose.yml up -d celery-worker

sleep 10

echo ""
echo "Step 6: Verifying all services..."
docker-compose -f docker-compose.yml ps

echo ""
echo "Step 7: Testing API endpoints..."
echo "Health check:"
curl -s http://localhost:8000/api/health | jq .

echo ""
echo "=== Testing Complete ==="
echo ""
echo "Services are running locally:"
echo "  - API: http://localhost:8000"
echo "  - Health: http://localhost:8000/api/health"
echo "  - Redis: localhost:6379"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""
echo "Cleanup:"
read -p "Do you want to stop the services now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.yml down
    echo "Services stopped."
else
    echo "Services are still running. Stop them manually with: docker-compose down"
fi

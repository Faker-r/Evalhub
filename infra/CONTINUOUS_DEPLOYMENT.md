# Continuous Deployment Guide

This document describes the continuous deployment (CD) system for the Evalhub backend, including AWS App Runner for the API and EC2 for Celery workers.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [How Deployments Work](#how-deployments-work)
4. [Local Testing](#local-testing)
5. [Secret Management](#secret-management)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)
8. [Monitoring](#monitoring)

## Architecture Overview

```
┌─────────────────┐
│ GitHub Actions  │
│  (Push to main) │
└────────┬────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
    ┌────▼─────┐                        ┌─────▼────┐
    │ Build &  │                        │  Deploy  │
    │ Push ECR │                        │   Jobs   │
    └────┬─────┘                        └─────┬────┘
         │                                     │
         │                        ┌────────────┴────────────┐
         │                        │                         │
    ┌────▼─────┐            ┌────▼────────┐         ┌──────▼──────┐
    │   ECR    │            │ App Runner  │         │ EC2 Celery  │
    │ Registry │◄───────────┤   Deploy    │         │   Deploy    │
    └──────────┘            └─────┬───────┘         └──────┬──────┘
                                  │                         │
                            ┌─────▼──────┐          ┌──────▼──────┐
                            │ App Runner │          │ EC2 Celery  │
                            │  Service   │          │  Workers    │
                            └─────┬──────┘          └──────┬──────┘
                                  │                         │
                            ┌─────▼─────────────────────────▼─────┐
                            │     AWS Secrets Manager              │
                            │     ElastiCache Redis                │
                            │     S3 Bucket                        │
                            └──────────────────────────────────────┘
```

### Components

- **GitHub Actions**: Automates build and deployment on push to `main`
- **Amazon ECR**: Stores Docker images for both App Runner and EC2
- **AWS App Runner**: Runs the FastAPI application (no Celery)
- **EC2 Instance**: Runs Celery workers using Docker Compose
- **AWS Secrets Manager**: Centralized secret storage
- **ElastiCache Redis**: Message broker for Celery
- **S3 Bucket**: Storage for evaluation artifacts

## Prerequisites

### AWS Resources (Managed by Terraform)

All infrastructure is defined in `infra/terraform/`:

- ECR repository: `evalhub-backend`
- Secrets Manager secrets: `evalhub/*`
- IAM roles for App Runner and EC2
- App Runner service
- EC2 instance with Docker
- ElastiCache Redis cluster

### GitHub Secrets

Configure these secrets in your GitHub repository (Settings → Secrets → Actions):

| Secret Name | Description |
|-------------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS access key for GitHub Actions |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for GitHub Actions |
| `AWS_REGION` | AWS region (default: `us-east-2`) |
| `EC2_SSH_PRIVATE_KEY` | Private SSH key for EC2 access |
| `EC2_HOST` | EC2 instance IP or hostname |

### Local Requirements

For local testing:
- Docker and Docker Compose
- AWS CLI configured
- `.env` file with required variables

## How Deployments Work

### Automatic Deployment Trigger

Deployments are triggered automatically when:
1. Code is pushed to the `main` branch
2. Changes are made to the `backend/` directory or CD workflow

### Deployment Pipeline

#### 1. Build and Push (5-10 minutes)

```yaml
jobs:
  build-and-push:
    - Checkout code
    - Configure AWS credentials
    - Login to ECR
    - Build Docker image with BuildKit cache
    - Tag with latest + git SHA
    - Push to ECR
```

**Image tags created:**
- `latest` - Always points to the most recent build
- `<git-sha>` - Specific commit for rollback capability

#### 2. Deploy App Runner (5-15 minutes)

```yaml
jobs:
  deploy-apprunner:
    - Trigger App Runner deployment
    - Wait for service to reach RUNNING state
    - Perform health check on /api/health
    - Output service URL
```

**App Runner configuration:**
- Pulls image from ECR automatically when new `latest` tag is pushed
- Environment variables loaded from Secrets Manager
- VPC connector for Redis access
- Auto-scaling enabled (1-10 instances)

#### 3. Deploy EC2 Celery (2-5 minutes)

```yaml
jobs:
  deploy-ec2-celery:
    - SSH to EC2 instance
    - Pull latest image from ECR
    - Fetch secrets from Secrets Manager
    - Update docker-compose configuration
    - Rolling restart of workers
    - Verify health
```

**Celery deployment:**
- 4 worker processes by default
- Rolling restart (minimal downtime)
- Health checks via Celery inspect

### Deployment Flow Diagram

```
Push to main
    │
    ├─► Lint & Test (CI)
    │
    ├─► Build Docker Image
    │       │
    │       └─► Push to ECR (latest + SHA)
    │
    ├─► Deploy App Runner
    │       │
    │       ├─► Pull image from ECR
    │       ├─► Load secrets from Secrets Manager
    │       ├─► Deploy new revision
    │       └─► Health check ✓
    │
    └─► Deploy EC2 Celery
            │
            ├─► SSH to EC2
            ├─► Pull image from ECR
            ├─► Fetch secrets
            ├─► docker-compose up -d
            └─► Verify workers ✓
```

## Local Testing

### Testing the Production Build Locally

Use the provided test script to validate your Docker setup before deploying:

```bash
cd backend
./deploy/test_local.sh
```

This script:
1. Builds the production Docker image
2. Starts Redis, API, and Celery worker locally
3. Runs health checks
4. Shows logs for verification

### Manual Local Testing

#### Build the image:

```bash
cd backend
docker build -t evalhub-backend:test \
  --build-arg GIT_COMMIT=$(git rev-parse HEAD) \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VERSION=test \
  .
```

#### Run with docker-compose:

```bash
export ECR_IMAGE_URI=evalhub-backend:test
docker-compose up -d
```

#### Verify health:

```bash
curl http://localhost:8000/api/health
docker-compose logs celery-worker
```

#### Cleanup:

```bash
docker-compose down
```

### Testing Production Compose Configuration

Test the EC2 production compose file:

```bash
export ECR_IMAGE_URI=evalhub-backend:test
export CELERY_WORKERS=2
docker-compose -f docker-compose.prod.yml up -d
```

## Secret Management

### Architecture

Secrets are stored in AWS Secrets Manager and accessed at runtime:

- **Terraform manages** secret resources (names, ARNs, policies)
- **Secret values** are never in Terraform state
- **App Runner** pulls secrets via `runtime_environment_secrets`
- **EC2** fetches secrets via AWS CLI on deployment

### Available Secrets

| Secret Name | Description |
|-------------|-------------|
| `evalhub/DATABASE_URL` | PostgreSQL connection string |
| `evalhub/JWT_SECRET` | JWT signing secret |
| `evalhub/AWS_ACCESS_KEY_ID` | AWS credentials for S3 |
| `evalhub/AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `evalhub/SUPABASE_URL` | Supabase project URL |
| `evalhub/SUPABASE_PUBLISHABLE_KEY` | Supabase public key |
| `evalhub/SUPABASE_SECRET_KEY` | Supabase secret key |
| `evalhub/SUPABASE_JWT_SECRET` | Supabase JWT verification |
| `evalhub/HF_TOKEN` | HuggingFace API token |
| `evalhub/REDIS_URL` | Redis connection URL |

### Updating Secrets

#### Method 1: Using sync script (recommended)

```bash
cd backend/deploy
./sync_secrets.sh
```

This reads your local `.env` file and syncs to AWS Secrets Manager.

#### Method 2: AWS Console

1. Go to AWS Secrets Manager console
2. Find the secret (e.g., `evalhub/DATABASE_URL`)
3. Click "Retrieve secret value"
4. Click "Edit"
5. Update the value
6. Save

#### Method 3: AWS CLI

```bash
aws secretsmanager put-secret-value \
  --region us-east-2 \
  --secret-id evalhub/DATABASE_URL \
  --secret-string "postgresql://..."
```

### After Updating Secrets

**App Runner**: Secrets are loaded at container start. Trigger a new deployment:

```bash
aws apprunner start-deployment \
  --service-arn $(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='evalhub-api-runner-github'].ServiceArn" --output text) \
  --region us-east-2
```

**EC2 Celery**: Secrets are fetched during deployment. Manually refresh:

```bash
ssh ec2-user@<ec2-host>
cd /opt/evalhub
./fetch_secrets.sh  # Or re-run deploy_ec2.sh
docker-compose -f docker-compose.prod.yml restart
```

## Rollback Procedures

### Rolling Back App Runner

#### Option 1: Redeploy previous image tag

```bash
# List recent images
aws ecr describe-images \
  --repository-name evalhub-backend \
  --region us-east-2 \
  --query 'sort_by(imageDetails,& imagePushedAt)[-5:]' \
  --output table

# Get service ARN
SERVICE_ARN=$(aws apprunner list-services \
  --region us-east-2 \
  --query "ServiceSummaryList[?ServiceName=='evalhub-api-runner-github'].ServiceArn" \
  --output text)

# Deploy specific image
aws apprunner update-service \
  --service-arn $SERVICE_ARN \
  --region us-east-2 \
  --source-configuration ImageRepository={ImageIdentifier=214863335048.dkr.ecr.us-east-2.amazonaws.com/evalhub-backend:<SHA>}
```

#### Option 2: Re-run previous GitHub Actions workflow

1. Go to GitHub Actions
2. Find the last successful deployment
3. Click "Re-run all jobs"

### Rolling Back EC2 Celery Workers

```bash
# SSH to EC2
ssh ec2-user@<ec2-host>

# Check available images
docker images | grep evalhub-backend

# Update docker-compose to use specific tag
export ECR_IMAGE_URI=214863335048.dkr.ecr.us-east-2.amazonaws.com/evalhub-backend:<SHA>

# Restart with old image
cd /opt/evalhub
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Verify
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs --tail=50
```

## Troubleshooting

### Build Failures

**Symptom**: GitHub Actions build job fails

**Common causes:**
- Dockerfile syntax error
- Missing dependencies in `pyproject.toml`
- Poetry lock file out of sync

**Fix:**
```bash
cd backend
poetry lock --no-update
git add poetry.lock
git commit -m "Update poetry.lock"
git push
```

### App Runner Deployment Failures

**Symptom**: App Runner deployment times out or fails health check

**Debug steps:**

1. Check App Runner logs:
```bash
aws logs tail /aws/apprunner/evalhub-api-runner-github/<service-id>/application --follow
```

2. Verify secrets are accessible:
```bash
aws apprunner describe-service \
  --service-arn <arn> \
  --query 'Service.SourceConfiguration.ImageRepository.ImageConfiguration.RuntimeEnvironmentSecrets'
```

3. Check VPC connectivity to Redis:
```bash
# From App Runner logs, look for connection errors
```

### EC2 Celery Deployment Failures

**Symptom**: Workers not starting or crashing

**Debug steps:**

1. SSH to EC2 and check logs:
```bash
ssh ec2-user@<ec2-host>
cd /opt/evalhub
docker-compose -f docker-compose.prod.yml logs
```

2. Check worker status:
```bash
docker-compose -f docker-compose.prod.yml ps
```

3. Verify secrets:
```bash
cat .env
```

4. Test Redis connectivity:
```bash
redis-cli -h <redis-endpoint> -p 6379 ping
```

5. Manually run worker:
```bash
docker-compose -f docker-compose.prod.yml run --rm celery-worker celery -A api.core.celery_app:celery_app inspect ping
```

### Image Pull Failures

**Symptom**: "Unable to pull image" errors

**Causes:**
- IAM role lacks ECR permissions
- Image doesn't exist in ECR
- Region mismatch

**Fix for App Runner:**
```bash
# Verify ECR access role has proper permissions
aws iam get-role-policy --role-name evalhub-apprunner-ecr-access-role --policy-name ECRAccess
```

**Fix for EC2:**
```bash
# Re-authenticate with ECR
ssh ec2-user@<ec2-host>
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 214863335048.dkr.ecr.us-east-2.amazonaws.com
```

### Secret Access Failures

**Symptom**: "Access denied" when fetching secrets

**Check IAM permissions:**

```bash
# For App Runner
aws iam list-attached-role-policies --role-name evalhub-secrets-role

# For EC2
aws iam list-attached-role-policies --role-name evalhub-ec2-celery-role
```

**Verify secrets exist:**
```bash
aws secretsmanager list-secrets \
  --region us-east-2 \
  --query 'SecretList[?starts_with(Name, `evalhub/`)].Name'
```

## Monitoring

### App Runner Metrics

CloudWatch metrics available:
- `2xxStatusResponses`
- `4xxStatusResponses`
- `5xxStatusResponses`
- `RequestCount`
- `Latency`
- `CPUUtilization`
- `MemoryUtilization`

View in CloudWatch console or CLI:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/AppRunner \
  --metric-name Latency \
  --dimensions Name=ServiceName,Value=evalhub-api-runner-github \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

### EC2 Celery Monitoring

**Check worker status:**
```bash
ssh ec2-user@<ec2-host>
cd /opt/evalhub
docker-compose -f docker-compose.prod.yml ps
```

**View worker logs:**
```bash
docker-compose -f docker-compose.prod.yml logs -f celery-worker
```

**Celery stats:**
```bash
docker-compose -f docker-compose.prod.yml exec celery-worker \
  celery -A api.core.celery_app:celery_app inspect stats
```

**Active tasks:**
```bash
docker-compose -f docker-compose.prod.yml exec celery-worker \
  celery -A api.core.celery_app:celery_app inspect active
```

### Deployment History

**GitHub Actions:**
- View workflow runs: https://github.com/Faker-r/Evalhub/actions

**App Runner:**
```bash
aws apprunner list-operations \
  --service-arn <arn> \
  --region us-east-2
```

**ECR Images:**
```bash
aws ecr describe-images \
  --repository-name evalhub-backend \
  --region us-east-2 \
  --query 'sort_by(imageDetails,& imagePushedAt)[-10:]' \
  --output table
```

## Best Practices

1. **Always test locally** before pushing to main
2. **Monitor deployments** in GitHub Actions
3. **Check health endpoints** after deployment
4. **Keep secrets in Secrets Manager**, never commit to Git
5. **Tag releases** for easier rollback
6. **Review logs** regularly for errors
7. **Set up CloudWatch alarms** for critical metrics
8. **Document changes** in commit messages
9. **Use feature branches** for risky changes
10. **Keep docker-compose.prod.yml** in sync with production needs

## Additional Resources

- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [Amazon ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Celery Documentation](https://docs.celeryproject.org/)

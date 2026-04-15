# Evalhub Terraform Infrastructure

This directory contains Terraform configuration for managing Evalhub's AWS infrastructure.

## Architecture

- **App Runner**: Runs the FastAPI backend service (ECR-based deployment)
- **EC2**: Runs Celery workers for async task processing
- **ECR**: Container registry for Docker images
- **Secrets Manager**: Centralized secret storage for all environment variables
- **S3**: Stores datasets, API keys, traces, and evaluation results
- **KMS**: Encrypts API keys stored in S3
- **ElastiCache Serverless (Redis)**: Celery broker and application cache
- **VPC Connector**: Enables App Runner to access VPC resources (Redis)
- **IAM Roles**: Service roles for App Runner and EC2 with least-privilege access

## Prerequisites

- Terraform >= 1.9.0
- AWS CLI configured with credentials
- Existing VPC with subnets in at least 2 availability zones

## Terraform Resources

### Managed Resources

| Resource | File | Description |
|----------|------|-------------|
| ECR Repository | `ecr.tf` | Container registry for backend images |
| Secrets Manager | `secrets_manager.tf` | All `evalhub/*` secrets |
| IAM Roles & Policies | `iam_roles.tf` | App Runner and EC2 service roles |
| App Runner Service | `imports_apprunner.tf` | FastAPI service (ECR-based) |
| EC2 Instance | `imports_ec2.tf` | Celery worker instance |
| ElastiCache Redis | `elasticache.tf` | Redis cluster |
| VPC Connector | `apprunner_connector.tf` | App Runner VPC access |
| Security Groups | `*.tf` | Network security rules |
| S3 Bucket | `imports_s3.tf` | Storage bucket |
| KMS Key | `imports_kms.tf` | Encryption key |

### New Resources (CD Implementation)

The following resources were added for continuous deployment:

1. **ECR Repository** (`ecr.tf`)
   - Repository: `evalhub-backend`
   - Image scanning enabled
   - Lifecycle policy: keep last 10 images

2. **Secrets Manager** (`secrets_manager.tf`)
   - All secrets with `evalhub/` prefix
   - Lifecycle rule: ignore secret values (managed separately)
   - Used by App Runner and EC2

3. **IAM Roles** (`iam_roles.tf`)
   - `evalhub-secrets-role`: App Runner instance role
   - `evalhub-apprunner-ecr-access-role`: ECR pull access for App Runner
   - `evalhub-ec2-celery-role`: EC2 instance role
   - `evalhub-ec2-celery-profile`: Instance profile for EC2
   - Policies for Secrets Manager and ECR access

4. **Updated App Runner** (`imports_apprunner.tf`)
   - Changed from GitHub source to ECR image repository
   - Auto-deployments enabled for `latest` tag
   - Runtime secrets from Secrets Manager
   - Runtime variables (AWS_REGION, S3_BUCKET_NAME, etc.)

5. **Updated EC2** (`imports_ec2.tf`)
   - IAM instance profile attached
   - User data for Docker/Docker Compose setup
   - Additional tags for deployment tracking

## Setup

### Initial Setup

1. Copy the example tfvars:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` with your values:
   - `vpc_id`: Your VPC ID
   - `private_subnet_ids`: At least 2 subnets in different AZs

3. Initialize Terraform:
   ```bash
   terraform init
   ```

4. Import existing resources (see Import Guide below)

5. Plan and apply:
   ```bash
   terraform plan
   terraform apply
   ```

## Import Guide

Before running `terraform apply`, import existing resources:

### Existing Resources to Import

```bash
# S3 bucket
terraform import aws_s3_bucket.evalhub evalhub-bucket
terraform import aws_s3_bucket_server_side_encryption_configuration.evalhub evalhub-bucket

# KMS key
terraform import aws_kms_key.evalhub 7b43a69b-9fe3-4239-beba-6c8bc4d2984e

# EC2 instance
terraform import aws_instance.celery_worker i-00c9fff40fd501441

# IAM role (existing)
terraform import aws_iam_role.apprunner_instance evalhub-secrets-role

# Secrets Manager (all evalhub/* secrets)
terraform import 'aws_secretsmanager_secret.evalhub["DATABASE_URL"]' evalhub/DATABASE_URL
terraform import 'aws_secretsmanager_secret.evalhub["JWT_SECRET"]' evalhub/JWT_SECRET
terraform import 'aws_secretsmanager_secret.evalhub["AWS_ACCESS_KEY_ID"]' evalhub/AWS_ACCESS_KEY_ID
terraform import 'aws_secretsmanager_secret.evalhub["AWS_SECRET_ACCESS_KEY"]' evalhub/AWS_SECRET_ACCESS_KEY
terraform import 'aws_secretsmanager_secret.evalhub["SUPABASE_URL"]' evalhub/SUPABASE_URL
terraform import 'aws_secretsmanager_secret.evalhub["SUPABASE_PUBLISHABLE_KEY"]' evalhub/SUPABASE_PUBLISHABLE_KEY
terraform import 'aws_secretsmanager_secret.evalhub["SUPABASE_SECRET_KEY"]' evalhub/SUPABASE_SECRET_KEY
terraform import 'aws_secretsmanager_secret.evalhub["SUPABASE_JWT_SECRET"]' evalhub/SUPABASE_JWT_SECRET
terraform import 'aws_secretsmanager_secret.evalhub["HF_TOKEN"]' evalhub/HF_TOKEN
terraform import 'aws_secretsmanager_secret.evalhub["REDIS_URL"]' evalhub/REDIS_URL

# App Runner service (import AFTER updating to ECR-based config)
# Note: This will require re-creating the service due to source type change
terraform import aws_apprunner_service.evalhub arn:aws:apprunner:us-east-2:214863335048:service/evalhub-api-runner-github/<service-id>
```

### Import Script

For convenience, use the import script:

```bash
cd /path/to/infra/terraform
./scripts/import_all.sh
```

## Remote State

Terraform state is stored in S3 with DynamoDB locking:
- Bucket: `evalhub-terraform-state`
- DynamoDB Table: `evalhub-terraform-locks`
- Region: `us-east-2`

## Outputs

After applying, get important values:

```bash
# Redis connection string
terraform output -raw redis_connection_string

# ECR repository URL
terraform output -raw ecr_repository_url

# App Runner service URL
terraform output -raw apprunner_service_url

# All secret ARNs
terraform output secrets_arns

# All outputs
terraform output
```

## Continuous Deployment Integration

This Terraform configuration integrates with the CD pipeline (see `infra/CONTINUOUS_DEPLOYMENT.md`):

1. **ECR Repository**: GitHub Actions pushes images here
2. **Secrets Manager**: App Runner and EC2 pull secrets at runtime
3. **App Runner**: Auto-deploys when new `latest` tag is pushed to ECR
4. **EC2 IAM Role**: Allows fetching secrets and pulling ECR images

### Deployment Flow

```
GitHub Actions → Build Image → Push to ECR (latest)
                                    ↓
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
            App Runner (auto)              EC2 (via SSH)
                    ↓                               ↓
          Pull from ECR                   Pull from ECR
                    ↓                               ↓
    Load secrets from Secrets Mgr    Fetch secrets from Secrets Mgr
                    ↓                               ↓
              Deploy API                  Deploy Celery
```

## Development

To make changes:

1. Update `.tf` files
2. Run `terraform fmt` to format
3. Run `terraform validate` to validate syntax
4. Run `terraform plan` to preview changes
5. Run `terraform apply` to apply changes

### Adding New Secrets

To add a new secret to Secrets Manager:

1. Add to `locals.evalhub_secrets` in `secrets_manager.tf`:
   ```hcl
   "NEW_SECRET" = {
     description = "Description of the secret"
   }
   ```

2. Create the secret in AWS:
   ```bash
   aws secretsmanager create-secret \
     --name evalhub/NEW_SECRET \
     --secret-string "value" \
     --region us-east-2
   ```

3. Import to Terraform:
   ```bash
   terraform import 'aws_secretsmanager_secret.evalhub["NEW_SECRET"]' evalhub/NEW_SECRET
   ```

4. Add to App Runner configuration in `imports_apprunner.tf`:
   ```hcl
   runtime_environment_secrets = {
     # ... existing secrets ...
     NEW_SECRET = aws_secretsmanager_secret.evalhub["NEW_SECRET"].arn
   }
   ```

5. Apply changes:
   ```bash
   terraform apply
   ```

## Updating App Runner / EC2

### Updating App Runner

App Runner now uses ECR and auto-deploys. To manually trigger:

```bash
SERVICE_ARN=$(terraform output -raw apprunner_service_arn)
aws apprunner start-deployment --service-arn $SERVICE_ARN --region us-east-2
```

### Updating EC2 Celery Workers

SSH to EC2 and run deployment script:

```bash
ssh ec2-user@$(terraform output -raw ec2_public_ip)
cd /opt/evalhub
./deploy_ec2.sh
```

Or trigger via GitHub Actions CD workflow (automatic on push to main).

## Troubleshooting

### App Runner Not Pulling Latest Image

```bash
# Check current image
aws apprunner describe-service \
  --service-arn $(terraform output -raw apprunner_service_arn) \
  --query 'Service.SourceConfiguration.ImageRepository.ImageIdentifier'

# Force new deployment
aws apprunner start-deployment \
  --service-arn $(terraform output -raw apprunner_service_arn)
```

### EC2 Cannot Pull from ECR

```bash
# Check IAM role
aws iam list-attached-role-policies --role-name evalhub-ec2-celery-role

# Test ECR login on EC2
ssh ec2-user@<ec2-ip>
aws ecr get-login-password --region us-east-2 | \
  docker login --username AWS --password-stdin \
  214863335048.dkr.ecr.us-east-2.amazonaws.com
```

### Secret Access Issues

```bash
# Verify IAM policy
terraform state show aws_iam_policy.secrets_manager_read

# Test secret access
aws secretsmanager get-secret-value \
  --secret-id evalhub/DATABASE_URL \
  --region us-east-2
```

### App Runner Service Recreation

If switching from GitHub to ECR source, App Runner may need recreation:

```bash
# This is expected and handled by Terraform
terraform apply
# Confirm recreation when prompted
```

## Security Notes

- The `terraform.tfvars` file contains sensitive information and is gitignored
- State file contains sensitive data - ensure S3 bucket has proper access controls
- Redis endpoint is marked as sensitive in outputs
- Secret **values** are NOT stored in Terraform state (only metadata/ARNs)
- IAM roles follow least-privilege principle
- ECR images are scanned for vulnerabilities on push

## Additional Documentation

- [Continuous Deployment Guide](../CONTINUOUS_DEPLOYMENT.md) - Full CD pipeline documentation
- [Deployment Summary](../DEPLOYMENT_SUMMARY.md) - Historical deployment notes
- [Terraform Cheatsheet](./CHEATSHEET.md) - Common Terraform commands

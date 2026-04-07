# Evalhub Terraform Infrastructure

This directory contains Terraform configuration for managing Evalhub's AWS infrastructure.

## Architecture

- **App Runner**: Runs the FastAPI backend service
- **EC2**: Runs Celery workers for async task processing
- **S3**: Stores datasets, API keys, traces, and evaluation results
- **KMS**: Encrypts API keys stored in S3
- **ElastiCache Serverless (Redis)**: Celery broker and application cache
- **VPC Connector**: Enables App Runner to access VPC resources (Redis)

## Prerequisites

- Terraform >= 1.9.0
- AWS CLI configured with credentials
- Existing VPC with subnets in at least 2 availability zones

## Setup

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

```bash
# S3 bucket
terraform import aws_s3_bucket.evalhub evalhub-bucket
terraform import aws_s3_bucket_server_side_encryption_configuration.evalhub evalhub-bucket

# KMS key
terraform import aws_kms_key.evalhub 7b43a69b-9fe3-4239-beba-6c8bc4d2984e

# EC2 instance
terraform import aws_instance.celery_worker i-00c9fff40fd501441

# App Runner service (import after VPC connector is created)
terraform import aws_apprunner_service.evalhub evalhub-api-runner-github
```

## Remote State

Terraform state is stored in S3 with DynamoDB locking:
- Bucket: `evalhub-terraform-state`
- DynamoDB Table: `evalhub-terraform-locks`

## Outputs

After applying, get important values:

```bash
# Redis connection string
terraform output -raw redis_connection_string

# All outputs
terraform output
```

## Updating App Runner / EC2 with Redis URL

After deploying Redis, update environment variables:

1. Get the Redis connection string:
   ```bash
   terraform output -raw redis_connection_string
   ```

2. Update App Runner service environment variables in AWS Console or via CLI

3. SSH to EC2 and update `.env` file with the new `REDIS_URL`

## Development

To make changes:

1. Update `.tf` files
2. Run `terraform plan` to preview changes
3. Run `terraform apply` to apply changes

## Security Notes

- The `terraform.tfvars` file contains sensitive information and is gitignored
- State file contains sensitive data - ensure S3 bucket has proper access controls
- Redis endpoint is marked as sensitive in outputs

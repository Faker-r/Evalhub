# Evalhub Terraform Infrastructure - Quick Start

This infrastructure-as-code setup manages your AWS resources for Evalhub.

## What This Creates

✅ **Already completed:**
- S3 bucket for Terraform state (`evalhub-terraform-state`)
- DynamoDB table for state locking (`evalhub-terraform-locks`)
- All Terraform configuration files

📦 **Will be imported:**
- Existing S3 bucket (`evalhub-bucket`)
- Existing KMS key
- Existing EC2 instance
- Existing App Runner service

🆕 **Will be created:**
- ElastiCache Serverless Redis cluster
- VPC connector for App Runner
- Security groups for Redis access
- Subnet groups for ElastiCache

## Prerequisites

1. **Install Terraform** (if not already installed):
   ```bash
   brew install terraform
   # OR download from: https://www.terraform.io/downloads
   ```

2. **Verify AWS credentials** are in `backend/.env`

## Quick Start (Option 1: Automated Script)

Run the automated import and deployment script:

```bash
cd infra/terraform
bash import_and_deploy.sh
```

This script will:
1. Initialize Terraform
2. Create VPC connector and security groups
3. Import all existing resources
4. Show you a plan of changes
5. Apply the infrastructure (with your confirmation)
6. Output the Redis connection string

## Manual Deployment (Option 2: Step by Step)

If you prefer manual control:

### Step 1: Initialize

```bash
cd infra/terraform
terraform init
```

### Step 2: Create VPC Connector First

```bash
terraform apply \
  -target=aws_security_group.apprunner_connector \
  -target=aws_security_group.redis \
  -target=aws_apprunner_vpc_connector.evalhub
```

### Step 3: Import Existing Resources

```bash
# S3 bucket
terraform import aws_s3_bucket.evalhub evalhub-bucket
terraform import aws_s3_bucket_server_side_encryption_configuration.evalhub evalhub-bucket

# KMS key
terraform import aws_kms_key.evalhub 7b43a69b-9fe3-4239-beba-6c8bc4d2984e

# EC2 instance
terraform import aws_instance.celery_worker i-00c9fff40fd501441

# App Runner service
terraform import aws_apprunner_service.evalhub evalhub-api-runner-github
```

### Step 4: Plan and Apply

```bash
terraform plan
terraform apply
```

## After Deployment

### 1. Get Redis Connection String

```bash
terraform output -raw redis_connection_string
```

This will output something like:
```
rediss://evalhub-redis-xxxxxx.serverless.use2.cache.amazonaws.com:6379
```

### 2. Update App Runner Environment

Update the App Runner service environment variables:

**Via AWS Console:**
1. Go to App Runner → Services → evalhub-api-runner-github
2. Configuration → Edit → Environment variables
3. Add/Update: `REDIS_URL=<value from terraform output>`
4. Deploy

**Via AWS CLI:**
```bash
REDIS_URL=$(terraform output -raw redis_connection_string)

# Get current config first
aws apprunner describe-service \
  --region us-east-2 \
  --service-arn <your-service-arn> \
  > current-config.json

# Then update with new REDIS_URL...
# (Manual step - App Runner update is complex via CLI)
```

### 3. Update EC2 Environment

SSH into your EC2 instance and update the `.env` file:

```bash
ssh -i ~/.ssh/evalhub.pem ubuntu@<ec2-ip>
cd /path/to/evalhub/backend
nano .env  # Update REDIS_URL with the new value
sudo systemctl restart celery  # or however you run Celery
```

## Verifying the Setup

### Check Redis Connectivity

From EC2:
```bash
redis-cli -h <redis-endpoint> -p 6379 --tls ping
```

From your code:
```python
import redis
client = redis.from_url("rediss://...")
client.ping()  # Should return True
```

### Check App Runner Connectivity

Monitor App Runner logs to ensure it connects to Redis successfully.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    VPC (existing)                    │
│                                                       │
│  ┌──────────────────────────────────────────────┐   │
│  │  ElastiCache Serverless (Redis)              │   │
│  │  - Engine: redis 7                            │   │
│  │  - TLS enabled                                │   │
│  │  - Multi-AZ                                   │   │
│  └───────────▲──────────────────────▲────────────┘   │
│              │                      │                │
│      ┌───────┴─────┐        ┌──────┴───────┐        │
│      │ SG: Redis   │        │              │        │
│      │ Port: 6379  │        │              │        │
│      └─────────────┘        │              │        │
│              ▲              │              │        │
│              │              │              │        │
│    ┌─────────┴──────┐  ┌────▼──────┐      │        │
│    │ VPC Connector  │  │    EC2    │      │        │
│    │ (App Runner)   │  │  Celery   │      │        │
│    └────────────────┘  └───────────┘      │        │
└─────────────────────────────────────────────────────┘
           │
           │ (Public access)
           ▼
    ┌──────────────┐
    │ App Runner   │
    │ Service      │
    └──────────────┘
```

## Common Issues

### Issue: Terraform state conflicts

**Solution:** The state is stored in S3 with DynamoDB locking. Multiple runs should be safe.

### Issue: Import says "already managed"

**Solution:** This is fine - the resource is already in state. Continue.

### Issue: App Runner can't connect to Redis

**Solution:**
1. Verify VPC connector is attached to the service
2. Check security group allows traffic from connector SG
3. Verify Redis is in the same VPC
4. Check Redis endpoint is correct (use `terraform output`)

### Issue: EC2 can't connect to Redis

**Solution:**
1. Verify EC2 security group is allowed in Redis SG
2. Check EC2 is in the same VPC as Redis
3. Test connectivity: `redis-cli -h <endpoint> -p 6379 --tls ping`

## Files Overview

- `versions.tf` - Terraform and provider versions, S3 backend config
- `providers.tf` - AWS provider configuration
- `variables.tf` - Input variables
- `terraform.tfvars` - Your actual values (gitignored)
- `data.tf` - Data sources for existing resources
- `outputs.tf` - Output values after apply
- `imports_*.tf` - Resources to be imported from existing AWS
- `elasticache.tf` - New ElastiCache Serverless Redis
- `apprunner_connector.tf` - New VPC connector for App Runner

## Cost Estimation

Approximate monthly costs:

- **ElastiCache Serverless:** ~$50-100/month (depends on usage)
- **VPC Connector:** ~$10/month
- **Existing resources:** No change

Total new infrastructure: ~$60-110/month

## Rolling Back

To destroy only the new infrastructure:

```bash
terraform destroy \
  -target=aws_elasticache_serverless_cache.redis \
  -target=aws_elasticache_subnet_group.redis \
  -target=aws_security_group.redis \
  -target=aws_apprunner_vpc_connector.evalhub \
  -target=aws_security_group.apprunner_connector
```

To destroy everything (including imported resources):
```bash
terraform destroy
```
**⚠️ Warning:** This will destroy ALL resources including S3, EC2, etc!

## Support

For issues or questions, refer to:
- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [ElastiCache Serverless Docs](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/WhatIs.html)
- [App Runner VPC Connector Docs](https://docs.aws.amazon.com/apprunner/latest/dg/network-vpc.html)

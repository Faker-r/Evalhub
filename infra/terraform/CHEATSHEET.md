# Evalhub Infrastructure - Quick Reference

## 🚀 Fast Deploy

```bash
# 1. Install Terraform (one-time)
brew install terraform

# 2. Deploy everything
cd infra/terraform
bash deploy.sh
```

## 📝 Common Commands

### Deployment
```bash
cd infra/terraform

# Initialize
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply

# Deploy specific resource
terraform apply -target=aws_elasticache_serverless_cache.redis
```

### Outputs
```bash
# Get Redis URL
terraform output -raw redis_connection_string

# All outputs
terraform output

# JSON format
terraform output -json
```

### State Management
```bash
# List resources
terraform state list

# Show resource details
terraform state show aws_elasticache_serverless_cache.redis

# Remove from state (doesn't delete resource)
terraform state rm aws_instance.celery_worker
```

### Imports
```bash
# S3
terraform import aws_s3_bucket.evalhub evalhub-bucket

# KMS
terraform import aws_kms_key.evalhub 7b43a69b-9fe3-4239-beba-6c8bc4d2984e

# EC2
terraform import aws_instance.celery_worker i-00c9fff40fd501441

# App Runner
terraform import aws_apprunner_service.evalhub evalhub-api-runner-github
```

### Destruction
```bash
# Destroy everything (CAREFUL!)
terraform destroy

# Destroy specific resource
terraform destroy -target=aws_elasticache_serverless_cache.redis
```

## 🔍 Debugging

### Check AWS Resources
```bash
# List App Runner services
aws apprunner list-services --region us-east-2

# Describe specific service
aws apprunner describe-service \
  --region us-east-2 \
  --service-arn <arn>

# List EC2 instances
aws ec2 describe-instances --region us-east-2

# Check Redis
aws elasticache describe-serverless-caches --region us-east-2
```

### Validate Configuration
```bash
cd infra/terraform

# Format code
terraform fmt -recursive

# Validate syntax
terraform validate

# Check for drift
terraform plan -refresh-only
```

### Logs
```bash
# App Runner logs (AWS Console)
# https://console.aws.amazon.com/apprunner → evalhub-api-runner-github → Logs

# EC2 Celery logs
ssh -i ~/.ssh/evalhub.pem ubuntu@<ec2-ip>
sudo journalctl -u celery -f
```

## 🧪 Testing Redis

### From Command Line
```bash
# Get endpoint
REDIS_HOST=$(cd infra/terraform && terraform output -json | jq -r '.redis_endpoint.value')

# Test connection
redis-cli -h $REDIS_HOST -p 6379 --tls ping
```

### From Python
```python
import redis
from api.core.config import settings

client = redis.from_url(settings.REDIS_URL, decode_responses=True)
print(client.ping())  # Should print: True
print(client.info('server'))
```

### From EC2
```bash
ssh -i ~/.ssh/evalhub.pem ubuntu@<ec2-ip>
cd ~/Evalhub/backend
poetry run python -c "
import redis
from api.core.config import settings
client = redis.from_url(settings.REDIS_URL)
print('Ping:', client.ping())
"
```

## 🔄 Update Environment Variables

### App Runner (Console)
1. Go to: https://console.aws.amazon.com/apprunner
2. Select: `evalhub-api-runner-github`
3. Configuration → Edit
4. Update `REDIS_URL=rediss://...`
5. Save & Deploy

### EC2
```bash
ssh -i ~/.ssh/evalhub.pem ubuntu@<ec2-ip>
nano ~/Evalhub/backend/.env  # Update REDIS_URL
sudo systemctl restart celery
```

## 📊 Monitoring

### AWS Console
- **ElastiCache:** https://console.aws.amazon.com/elasticache
- **App Runner:** https://console.aws.amazon.com/apprunner
- **EC2:** https://console.aws.amazon.com/ec2
- **CloudWatch:** https://console.aws.amazon.com/cloudwatch

### CLI
```bash
# ElastiCache metrics
aws cloudwatch get-metric-statistics \
  --region us-east-2 \
  --namespace AWS/ElastiCache \
  --metric-name ECPUUtilization \
  --dimensions Name=CacheName,Value=evalhub-redis \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average

# App Runner service status
aws apprunner list-operations \
  --region us-east-2 \
  --service-arn <arn>
```

## 💰 Cost Check

```bash
# AWS Cost Explorer (Console)
# https://console.aws.amazon.com/cost-management/home

# CLI - Current month costs
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

## 🆘 Emergency Rollback

```bash
# 1. Revert app configs to local Redis
# In App Runner & EC2: REDIS_URL=redis://localhost:6379/0

# 2. Destroy ElastiCache (to stop costs)
cd infra/terraform
terraform destroy \
  -target=aws_elasticache_serverless_cache.redis \
  -target=aws_elasticache_subnet_group.redis \
  -target=aws_security_group.redis
```

## 📚 Documentation

- **Setup:** `README.md`
- **Quick Start:** `QUICKSTART.md`
- **Post-Deploy:** `POST_DEPLOYMENT.md`
- **Summary:** `../DEPLOYMENT_SUMMARY.md`

## 🔐 Credentials

AWS credentials are loaded from `backend/.env`:
```bash
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-2
```

Or use AWS CLI default profile:
```bash
aws configure
```

## 🎯 Health Check

Quick verification after deployment:

```bash
# ✅ Terraform
cd infra/terraform && terraform validate && echo "OK"

# ✅ Redis
redis-cli -h $(terraform output -raw redis_endpoint) -p 6379 --tls ping

# ✅ App Runner
aws apprunner describe-service --region us-east-2 \
  --service-arn $(terraform output -raw apprunner_service_arn) \
  --query 'Service.Status' --output text

# ✅ EC2
aws ec2 describe-instances --region us-east-2 \
  --instance-ids $(terraform output -raw ec2_instance_id) \
  --query 'Reservations[0].Instances[0].State.Name' --output text
```

All should return successful status!

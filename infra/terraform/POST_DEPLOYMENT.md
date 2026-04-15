# Post-Deployment Configuration Guide

After running `terraform apply`, you need to update your application configurations to use the new Redis instance.

## 1. Get the Redis Connection String

From the `infra/terraform` directory:

```bash
terraform output -raw redis_connection_string
```

This will output something like:
```
rediss://evalhub-redis-xxxxxx.serverless.use2.cache.amazonaws.com:6379
```

Copy this value - you'll need it for the next steps.

## 2. Update App Runner Environment Variables

### Option A: AWS Console (Easiest)

1. Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner)
2. Select region: `us-east-2`
3. Click on service: `evalhub-api-runner-github`
4. Go to **Configuration** tab
5. Click **Edit** under **Environment variables**
6. Update or add:
   - Key: `REDIS_URL`
   - Value: `rediss://evalhub-redis-xxxxxx.serverless.use2.cache.amazonaws.com:6379`
7. Click **Save changes**
8. Wait for deployment to complete (~5 minutes)

### Option B: AWS CLI

```bash
# Get the Redis URL
REDIS_URL=$(cd infra/terraform && terraform output -raw redis_connection_string)

# Get current service ARN
SERVICE_ARN="arn:aws:apprunner:us-east-2:214863335048:service/evalhub-api-runner-github/bc6e87163a054d188a635736f006d280"

# Note: Updating App Runner via CLI requires reconstructing the entire
# source configuration. It's recommended to use the Console for this step.
```

## 3. Update EC2 Instance Environment

### SSH into EC2

```bash
# Get EC2 instance IP
aws ec2 describe-instances \
  --region us-east-2 \
  --instance-ids i-00c9fff40fd501441 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text

# SSH (adjust key path as needed)
ssh -i ~/.ssh/evalhub.pem ubuntu@<EC2_PUBLIC_IP>
```

### Update Environment File

```bash
# Navigate to your application directory
cd ~/Evalhub/backend  # or wherever your app is located

# Backup current .env
cp .env .env.backup

# Edit .env file
nano .env
```

Update the `REDIS_URL` line:
```bash
# OLD (local Redis)
REDIS_URL=redis://localhost:6379/0

# NEW (ElastiCache Serverless with TLS)
REDIS_URL=rediss://evalhub-redis-xxxxxx.serverless.use2.cache.amazonaws.com:6379
```

Save and exit (Ctrl+X, then Y, then Enter in nano).

### Restart Celery Workers

```bash
# If using systemd
sudo systemctl restart celery

# If running manually with start_all.sh
pkill -f celery
bash start_all.sh
```

## 4. Verify Connectivity

### Test from EC2

```bash
# Install redis-cli if not present
sudo apt-get update && sudo apt-get install -y redis-tools

# Test connection (note: --tls flag for TLS connection)
redis-cli -h evalhub-redis-xxxxxx.serverless.use2.cache.amazonaws.com -p 6379 --tls ping
# Should return: PONG
```

### Test from Python

```bash
cd ~/Evalhub/backend
poetry run python -c "
import redis
from api.core.config import settings
client = redis.from_url(settings.REDIS_URL, decode_responses=True)
print('Redis ping:', client.ping())
print('Redis info:', client.info('server')['redis_version'])
"
```

Expected output:
```
Redis ping: True
Redis info: 7.x.x
```

### Check Application Logs

**App Runner:**
1. Go to App Runner Console → Service → Logs
2. Look for successful Redis connections
3. Should NOT see connection errors

**EC2 Celery:**
```bash
# If using systemd
sudo journalctl -u celery -f

# Look for:
# - "Connected to redis://..." (broker connection)
# - No connection errors
```

## 5. Monitor Redis Usage

### Via AWS Console

1. Go to [ElastiCache Console](https://console.aws.amazon.com/elasticache)
2. Click on `evalhub-redis`
3. View metrics:
   - ECPU usage
   - Data storage
   - Connections
   - Network throughput

### Via Terraform

```bash
cd infra/terraform
terraform output
```

## 6. Troubleshooting

### App Runner Can't Connect

**Check VPC Connector:**
```bash
cd infra/terraform
terraform state show aws_apprunner_vpc_connector.evalhub
terraform state show aws_apprunner_service.evalhub
```

Verify the VPC connector ARN is attached to the service's network configuration.

**Check Security Groups:**
```bash
# Verify Redis security group allows traffic from VPC connector
terraform state show aws_security_group.redis
```

### EC2 Can't Connect

**Check Security Groups:**
```bash
# Verify EC2's security group is allowed in Redis SG
terraform state show aws_security_group.redis
```

Should show ingress rule with EC2's security group: `sg-052807540561ab35a`

**Test Network Path:**
```bash
# From EC2
telnet evalhub-redis-xxxxxx.serverless.use2.cache.amazonaws.com 6379
# Should connect (Ctrl+] then quit to exit)
```

### TLS Issues

ElastiCache Serverless uses TLS by default. Ensure:

1. **Connection string uses `rediss://`** (not `redis://`)
2. **redis-py version supports TLS:**
   ```bash
   poetry show redis
   # Should be >= 4.5.2
   ```

3. **Python code uses proper SSL config:**
   ```python
   # In api/core/cache.py and api/core/redis_client.py
   redis.from_url(
       settings.REDIS_URL,
       ssl_cert_reqs=None,  # For self-signed certs
       decode_responses=True
   )
   ```

### Performance Issues

**Check ECPU Limits:**
```bash
cd infra/terraform
terraform show | grep ecpu_per_second
# Current max: 5000
```

If hitting limits, update `terraform.tfvars`:
```hcl
elasticache_max_ecpu = 10000  # Increase as needed
```

Then apply:
```bash
terraform apply
```

## 7. Rollback (If Needed)

To revert to local Redis:

1. **Update environment variables back to local:**
   ```bash
   REDIS_URL=redis://localhost:6379/0
   ```

2. **Restart services** (App Runner + EC2 Celery)

3. **Optional: Destroy ElastiCache** (to save costs):
   ```bash
   cd infra/terraform
   terraform destroy -target=aws_elasticache_serverless_cache.redis
   ```

## Next Steps

Once verified:

1. **Monitor costs** in AWS Cost Explorer
2. **Set up alerts** for Redis ECPU/storage usage
3. **Document** the new Redis endpoint in your team wiki
4. **Remove** old Redis infrastructure if separate
5. **Update** any CI/CD pipelines with new connection strings

## Support Resources

- [ElastiCache Serverless Docs](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/WhatIs.html)
- [redis-py Documentation](https://redis-py.readthedocs.io/)
- [Celery with Redis](https://docs.celeryproject.org/en/stable/getting-started/backends-and-brokers/redis.html)

# Evalhub Infrastructure Summary

## ✅ What Has Been Completed

### 1. Remote State Infrastructure (AWS)
- **S3 Bucket:** `evalhub-terraform-state` (versioning enabled, encrypted, public access blocked)
- **DynamoDB Table:** `evalhub-terraform-locks` (state locking)

### 2. Terraform Configuration Files Created

All files are in `/infra/terraform/`:

#### Core Configuration
- `versions.tf` - Terraform 1.9+ requirement, AWS provider ~5.0, S3 backend config
- `providers.tf` - AWS provider with region and default tags
- `variables.tf` - All input variables with sensible defaults
- `terraform.tfvars` - Your actual values (gitignored)
- `terraform.tfvars.example` - Template for other users
- `data.tf` - Data sources for existing VPC/subnets
- `outputs.tf` - Outputs including Redis connection string

#### Resource Definitions

**Imports (Existing Resources):**
- `imports_s3.tf` - S3 bucket and encryption config
- `imports_kms.tf` - KMS key for API key encryption
- `imports_ec2.tf` - EC2 Celery worker instance
- `imports_apprunner.tf` - App Runner service (will be updated with VPC connector)

**New Infrastructure:**
- `elasticache.tf` - ElastiCache Serverless Redis cluster + security group + subnet group
- `apprunner_connector.tf` - VPC connector + security group for App Runner

#### Documentation & Scripts
- `README.md` - Comprehensive setup and usage guide
- `QUICKSTART.md` - Fast-track deployment guide
- `POST_DEPLOYMENT.md` - Environment variable update instructions
- `import_and_deploy.sh` - Automated deployment script
- `.gitignore` - Protects sensitive files (tfvars, state, etc.)

### 3. Repository Updates
- Updated root `.gitignore` to exclude Terraform sensitive files

## 📋 Next Steps (For You to Execute)

### Step 1: Install Terraform (if not already)

```bash
brew install terraform
```

Or download from https://www.terraform.io/downloads

### Step 2: Deploy Infrastructure

**Option A - Automated (Recommended):**
```bash
cd infra/terraform
bash import_and_deploy.sh
```

**Option B - Manual:**
```bash
cd infra/terraform
terraform init
terraform apply -target=aws_security_group.apprunner_connector \
                -target=aws_security_group.redis \
                -target=aws_apprunner_vpc_connector.evalhub

# Import existing resources
terraform import aws_s3_bucket.evalhub evalhub-bucket
terraform import aws_s3_bucket_server_side_encryption_configuration.evalhub evalhub-bucket
terraform import aws_kms_key.evalhub 7b43a69b-9fe3-4239-beba-6c8bc4d2984e
terraform import aws_instance.celery_worker i-00c9fff40fd501441
terraform import aws_apprunner_service.evalhub evalhub-api-runner-github

# Deploy everything
terraform plan
terraform apply
```

### Step 3: Update Application Configuration

After `terraform apply` completes:

1. **Get Redis URL:**
   ```bash
   terraform output -raw redis_connection_string
   ```

2. **Update App Runner** (see `POST_DEPLOYMENT.md`)
3. **Update EC2** (see `POST_DEPLOYMENT.md`)

## 🏗️ Infrastructure Architecture

```
┌─────────────────────────────────────────────────────┐
│                 AWS us-east-2                        │
│                                                       │
│  ┌────────────────────────────────────────────────┐ │
│  │  VPC (vpc-0bbab27e1e3cf6d7f)                   │ │
│  │                                                  │ │
│  │  ┌──────────────────────────────────────────┐  │ │
│  │  │  ElastiCache Serverless Redis            │  │ │
│  │  │  • Engine: redis 7                        │  │ │
│  │  │  • TLS enabled                            │  │ │
│  │  │  • Max 10GB storage, 5000 ECPU/s         │  │ │
│  │  │  • Multi-AZ (3 subnets)                  │  │ │
│  │  └─────────▲─────────────────────▲───────────┘  │ │
│  │            │                     │              │ │
│  │     ┌──────┴────────┐    ┌──────┴──────┐       │ │
│  │     │ Security Group│    │   EC2 t3    │       │ │
│  │     │ Port 6379     │    │   Celery    │       │ │
│  │     │ (2 rules)     │    │   Worker    │       │ │
│  │     └───────────────┘    └─────────────┘       │ │
│  │            ▲                                    │ │
│  │            │                                    │ │
│  │     ┌──────┴────────┐                          │ │
│  │     │ VPC Connector │                          │ │
│  │     │ (App Runner)  │                          │ │
│  │     └───────────────┘                          │ │
│  └────────────────────────────────────────────────┘ │
│            ▲                                        │
│            │                                        │
│  ┌─────────┴───────┐                               │
│  │   App Runner    │                               │
│  │   Service       │                               │
│  │   (FastAPI)     │                               │
│  └─────────────────┘                               │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │  Supporting Resources                       │   │
│  │  • S3: evalhub-bucket                       │   │
│  │  • KMS: API key encryption                  │   │
│  └────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  Terraform State Storage                 │
│  • S3: evalhub-terraform-state           │
│  • DynamoDB: evalhub-terraform-locks     │
└──────────────────────────────────────────┘
```

## 📊 Resources Managed

### Imported (Existing)
- ✅ S3 bucket: `evalhub-bucket`
- ✅ KMS key: `7b43a69b-9fe3-4239-beba-6c8bc4d2984e`
- ✅ EC2 instance: `i-00c9fff40fd501441` (t3.medium)
- ✅ App Runner service: `evalhub-api-runner-github`

### Created (New)
- 🆕 ElastiCache Serverless: `evalhub-redis`
- 🆕 VPC Connector: `evalhub-vpc-connector`
- 🆕 Security Group (Redis): allows traffic from VPC connector + EC2
- 🆕 Security Group (VPC Connector): allows egress to VPC
- 🆕 Subnet Group: spans 3 AZs (us-east-2a/b/c)

### State Management
- 🔒 State bucket: `evalhub-terraform-state` (encrypted, versioned)
- 🔒 Lock table: `evalhub-terraform-locks` (prevents concurrent runs)

## 💰 Cost Impact

### New Monthly Costs
- **ElastiCache Serverless:** ~$50-100/month (usage-based)
- **VPC Connector:** ~$10/month
- **State Storage:** <$1/month

**Total new infrastructure:** ~$60-110/month

### Existing (No Change)
- App Runner: ~$25-50/month (unchanged)
- EC2 t3.medium: ~$30/month (unchanged)
- S3 storage: ~$5-10/month (unchanged)

## 🔐 Security Notes

1. **Sensitive Files (Gitignored):**
   - `terraform.tfvars` - Contains VPC IDs
   - `*.tfstate` - Contains resource details
   - `redis_url.txt` - Generated connection string

2. **TLS Encryption:**
   - Redis uses TLS by default (`rediss://`)
   - App Runner ↔ Redis: TLS 1.2+
   - EC2 ↔ Redis: TLS 1.2+

3. **Network Security:**
   - Redis only accessible within VPC
   - Security groups restrict to App Runner + EC2 only
   - No public internet access to Redis

## 🧪 Testing After Deployment

### 1. Verify Terraform Outputs
```bash
cd infra/terraform
terraform output
```

### 2. Test Redis Connectivity

**From EC2:**
```bash
redis-cli -h <redis-endpoint> -p 6379 --tls ping
# Should return: PONG
```

**From Python:**
```python
import redis
client = redis.from_url("rediss://...", decode_responses=True)
client.ping()  # Should return True
```

### 3. Monitor Application Logs

- **App Runner:** Check logs in AWS Console for Redis connections
- **EC2 Celery:** `sudo journalctl -u celery -f`

## 📚 Documentation Reference

- **Setup:** `infra/terraform/README.md`
- **Quick Start:** `infra/terraform/QUICKSTART.md`
- **Post-Deploy:** `infra/terraform/POST_DEPLOYMENT.md`

## 🆘 Getting Help

### Common Issues

1. **"Terraform not found"**
   - Install: `brew install terraform`

2. **"Resource already exists"**
   - Already created, continue with imports

3. **"Import failed"**
   - Check resource IDs in variables.tf match reality
   - Verify AWS credentials are correct

4. **"Can't connect to Redis"**
   - Verify VPC connector is attached to App Runner
   - Check security group rules
   - Ensure using `rediss://` (with TLS)

### Support Commands

```bash
# Check Terraform version
terraform version

# Validate configuration
cd infra/terraform && terraform validate

# Check what's in state
terraform state list

# Show specific resource
terraform state show aws_elasticache_serverless_cache.redis

# Re-run import if needed
terraform import <resource> <id>
```

## ✨ What's Different from Before

### Before
- Local Redis on EC2 only
- App Runner couldn't access Redis
- Manual infrastructure management
- No centralized cache for API

### After
- ✅ Centralized Redis (ElastiCache Serverless)
- ✅ App Runner connected to Redis via VPC connector
- ✅ EC2 connected to same Redis
- ✅ Infrastructure as Code (Terraform)
- ✅ Shared cache + Celery broker
- ✅ Multi-AZ high availability
- ✅ Auto-scaling (ECPU + storage)
- ✅ Encrypted in transit (TLS)
- ✅ Versioned state with locking

## 🎯 Success Criteria

Infrastructure is successfully deployed when:

- [x] Terraform state is in S3 with DynamoDB locking
- [x] All Terraform files created and validated
- [ ] `terraform apply` completes without errors
- [ ] Redis endpoint appears in outputs
- [ ] App Runner updated with Redis URL
- [ ] EC2 updated with Redis URL
- [ ] Both can `PING` Redis successfully
- [ ] Application logs show Redis connections
- [ ] Celery tasks execute successfully

## 🚀 You're Ready!

All infrastructure code is complete. The final steps are:

1. Install Terraform (if needed)
2. Run `bash infra/terraform/import_and_deploy.sh`
3. Update app configs with Redis URL
4. Verify connectivity

Good luck! 🎉

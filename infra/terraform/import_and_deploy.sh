#!/bin/bash
# Evalhub Infrastructure Import and Deployment Script
#
# Prerequisites:
# - Terraform >= 1.9.0 installed
# - AWS CLI configured with proper credentials
# - Run this from the infra/terraform directory
#
# Usage: bash import_and_deploy.sh

set -e

cd "$(dirname "$0")"

echo "========================================="
echo "Evalhub Infrastructure Setup"
echo "========================================="
echo ""

# Load AWS credentials from backend .env
if [ -f "../../backend/.env" ]; then
    export $(grep -v '^#' ../../backend/.env | grep -E 'AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY|AWS_REGION' | xargs)
    echo "✓ Loaded AWS credentials from backend/.env"
else
    echo "⚠ Warning: backend/.env not found, using default AWS credentials"
fi

# Check Terraform installation
if ! command -v terraform &> /dev/null; then
    echo "✗ Error: Terraform is not installed"
    echo "  Install it from: https://www.terraform.io/downloads"
    echo "  Or run: brew install terraform"
    exit 1
fi

echo "✓ Terraform version: $(terraform version -json | jq -r '.terraform_version')"
echo ""

# Initialize Terraform
echo "Step 1: Initializing Terraform..."
terraform init
echo "✓ Terraform initialized"
echo ""

# Create VPC connector and security groups first (these don't require import)
echo "Step 2: Creating VPC connector and security groups..."
terraform apply -target=aws_security_group.apprunner_connector \
               -target=aws_security_group.redis \
               -target=aws_apprunner_vpc_connector.evalhub \
               -auto-approve
echo "✓ VPC connector created"
echo ""

# Import existing resources
echo "Step 3: Importing existing resources..."

# S3 bucket
echo "  Importing S3 bucket..."
terraform import -input=false aws_s3_bucket.evalhub evalhub-bucket 2>&1 | grep -v "Resource already managed" || true
terraform import -input=false aws_s3_bucket_server_side_encryption_configuration.evalhub evalhub-bucket 2>&1 | grep -v "Resource already managed" || true

# KMS key
echo "  Importing KMS key..."
terraform import -input=false aws_kms_key.evalhub 7b43a69b-9fe3-4239-beba-6c8bc4d2984e 2>&1 | grep -v "Resource already managed" || true

# EC2 instance
echo "  Importing EC2 instance..."
terraform import -input=false aws_instance.celery_worker i-00c9fff40fd501441 2>&1 | grep -v "Resource already managed" || true

# App Runner service (Terraform import ID must be the full service ARN, not the service name)
echo "  Importing App Runner service..."
APPRUNNER_SERVICE_NAME="${APPRUNNER_SERVICE_NAME:-evalhub-api-runner-github}"
REGION="${AWS_REGION:-us-east-2}"
APPRUNNER_ARN=$(aws apprunner list-services --region "$REGION" \
  --query "ServiceSummaryList[?ServiceName=='${APPRUNNER_SERVICE_NAME}'].ServiceArn | [0]" \
  --output text)
if [ -z "$APPRUNNER_ARN" ] || [ "$APPRUNNER_ARN" = "None" ]; then
  echo "  ✗ No App Runner service named ${APPRUNNER_SERVICE_NAME} in ${REGION}"
  exit 1
fi
terraform import -input=false aws_apprunner_service.evalhub "$APPRUNNER_ARN" 2>&1 | grep -v "Resource already managed" || true

echo "✓ Resources imported"
echo ""

# Plan to show what will be created
echo "Step 4: Planning infrastructure changes..."
terraform plan -out=tfplan
echo ""

# Ask for confirmation
read -p "Do you want to apply these changes? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Aborted by user"
    exit 0
fi

# Apply the plan
echo "Step 5: Applying infrastructure changes..."
terraform apply tfplan
echo ""

# Show outputs
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
terraform output
echo ""

# Save Redis URL to a file for easy reference
REDIS_URL=$(terraform output -raw redis_connection_string 2>/dev/null || echo "")
if [ -n "$REDIS_URL" ]; then
    echo "Redis connection string saved to redis_url.txt"
    echo "$REDIS_URL" > redis_url.txt
    chmod 600 redis_url.txt
    
    echo ""
    echo "Next Steps:"
    echo "1. Update App Runner environment variables with:"
    echo "   REDIS_URL=$REDIS_URL"
    echo "2. SSH to EC2 and update ~/.env with the same REDIS_URL"
    echo "3. Restart App Runner and EC2 services"
fi

#!/bin/bash
# Quick deployment script - run this after installing Terraform
# Usage: bash deploy.sh

set -e

echo "🚀 Evalhub Infrastructure Deployment"
echo "===================================="
echo ""

# Check prerequisites
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not installed"
    echo "   Install with: brew install terraform"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not installed"
    echo "   Install with: brew install awscli"
    exit 1
fi

echo "✅ Prerequisites OK"
echo ""

# Load environment
if [ -f "../../backend/.env" ]; then
    export $(grep -v '^#' ../../backend/.env | grep -E 'AWS_' | xargs)
fi

cd "$(dirname "$0")"

# Run the main script
exec bash import_and_deploy.sh

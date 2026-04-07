#!/bin/bash
set -e

AWS_REGION="${AWS_REGION:-us-east-2}"
ENV_FILE="${ENV_FILE:-.env}"

echo "=== Secrets Sync Script ==="
echo "This script syncs secrets from local .env to AWS Secrets Manager"
echo "Region: $AWS_REGION"
echo ""

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: Environment file $ENV_FILE not found"
    exit 1
fi

read -p "This will update secrets in AWS Secrets Manager. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

SECRET_MAPPINGS=(
    "DATABASE_URL:evalhub/DATABASE_URL"
    "JWT_SECRET:evalhub/JWT_SECRET"
    "AWS_ACCESS_KEY_ID:evalhub/AWS_ACCESS_KEY_ID"
    "AWS_SECRET_ACCESS_KEY:evalhub/AWS_SECRET_ACCESS_KEY"
    "SUPABASE_URL:evalhub/SUPABASE_URL"
    "SUPABASE_PUBLISHABLE_KEY:evalhub/SUPABASE_PUBLISHABLE_KEY"
    "SUPABASE_SECRET_KEY:evalhub/SUPABASE_SECRET_KEY"
    "SUPABASE_JWT_SECRET:evalhub/SUPABASE_JWT_SECRET"
    "HF_TOKEN:evalhub/HF_TOKEN"
    "REDIS_URL:evalhub/REDIS_URL"
)

echo ""
echo "Syncing secrets..."

# AWS CLI v2 treats --secret-string values starting with https:// as URLs to fetch.
# Write the value to a file and use file:// so Supabase URLs (and similar) are stored literally.
put_secret_value() {
    local secret_name="$1"
    local secret_value="$2"
    local tmp
    tmp="$(mktemp)"
    printf '%s' "$secret_value" > "$tmp"
    aws secretsmanager put-secret-value \
        --region "$AWS_REGION" \
        --secret-id "$secret_name" \
        --secret-string "file://${tmp}" \
        --output text > /dev/null
    rm -f "$tmp"
}

while IFS= read -r line; do
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    
    if [[ "$line" =~ ^([A-Z_]+)=(.*)$ ]]; then
        env_key="${BASH_REMATCH[1]}"
        env_value="${BASH_REMATCH[2]}"
        
        env_value=$(echo "$env_value" | sed 's/^["'\'']//' | sed 's/["'\'']$//')
        
        for mapping in "${SECRET_MAPPINGS[@]}"; do
            IFS=':' read -r key secret_name <<< "$mapping"
            
            if [ "$key" = "$env_key" ]; then
                echo "Updating $secret_name..."
                put_secret_value "$secret_name" "$env_value"
                echo "  ✓ Updated $secret_name"
                break
            fi
        done
    fi
done < "$ENV_FILE"

echo ""
echo "=== Sync Complete ==="
echo "All secrets have been updated in AWS Secrets Manager"
echo ""
echo "Verify with:"
echo "  aws secretsmanager list-secrets --region $AWS_REGION --query 'SecretList[?starts_with(Name, \`evalhub/\`)].Name'"

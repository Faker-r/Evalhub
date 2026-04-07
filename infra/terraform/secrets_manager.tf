locals {
  evalhub_secrets = {
    "DATABASE_URL" = {
      description = "PostgreSQL database connection URL"
    }
    "JWT_SECRET" = {
      description = "JWT secret for authentication"
    }
    "AWS_ACCESS_KEY_ID" = {
      description = "AWS access key for S3 and other services"
    }
    "AWS_SECRET_ACCESS_KEY" = {
      description = "AWS secret access key"
    }
    "SUPABASE_URL" = {
      description = "Supabase project URL"
    }
    "SUPABASE_PUBLISHABLE_KEY" = {
      description = "Supabase publishable API key"
    }
    "SUPABASE_SECRET_KEY" = {
      description = "Supabase secret API key"
    }
    "SUPABASE_JWT_SECRET" = {
      description = "Supabase JWT secret for token verification"
    }
    "HF_TOKEN" = {
      description = "HuggingFace API token"
    }
    "REDIS_URL" = {
      description = "Redis connection URL"
    }
  }
}

resource "aws_secretsmanager_secret" "evalhub" {
  for_each = local.evalhub_secrets

  name        = "evalhub/${each.key}"
  description = each.value.description

  tags = {
    Name        = "evalhub/${each.key}"
    Project     = "evalhub"
    ManagedBy   = "terraform"
    Environment = "production"
  }
}

resource "aws_secretsmanager_secret_version" "evalhub" {
  for_each = local.evalhub_secrets

  secret_id     = aws_secretsmanager_secret.evalhub[each.key].id
  secret_string = "PLACEHOLDER"

  lifecycle {
    ignore_changes = [secret_string]
  }
}

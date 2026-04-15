# Import existing App Runner service

resource "aws_apprunner_service" "evalhub" {
  service_name = var.apprunner_service_name

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_access.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.backend.repository_url}:latest"
      image_repository_type = "ECR"

      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          AWS_REGION     = var.aws_region
          S3_BUCKET_NAME = var.s3_bucket_name
          CELERY_WORKERS = "0"
          PORT           = "8000"
        }
        runtime_environment_secrets = {
          DATABASE_URL             = aws_secretsmanager_secret.evalhub["DATABASE_URL"].arn
          JWT_SECRET               = aws_secretsmanager_secret.evalhub["JWT_SECRET"].arn
          AWS_ACCESS_KEY_ID        = aws_secretsmanager_secret.evalhub["AWS_ACCESS_KEY_ID"].arn
          AWS_SECRET_ACCESS_KEY    = aws_secretsmanager_secret.evalhub["AWS_SECRET_ACCESS_KEY"].arn
          SUPABASE_URL             = aws_secretsmanager_secret.evalhub["SUPABASE_URL"].arn
          SUPABASE_PUBLISHABLE_KEY = aws_secretsmanager_secret.evalhub["SUPABASE_PUBLISHABLE_KEY"].arn
          SUPABASE_SECRET_KEY      = aws_secretsmanager_secret.evalhub["SUPABASE_SECRET_KEY"].arn
          SUPABASE_JWT_SECRET      = aws_secretsmanager_secret.evalhub["SUPABASE_JWT_SECRET"].arn
          HF_TOKEN                 = aws_secretsmanager_secret.evalhub["HF_TOKEN"].arn
          REDIS_URL                = aws_secretsmanager_secret.evalhub["REDIS_URL"].arn
          CELERY_BROKER_URL        = aws_secretsmanager_secret.evalhub["CELERY_BROKER_URL"].arn
        }
      }
    }

    auto_deployments_enabled = true
  }

  instance_configuration {
    cpu               = "1024"
    memory            = "2048"
    instance_role_arn = aws_iam_role.apprunner_instance.arn
  }

  health_check_configuration {
    protocol            = "TCP"
    path                = "/"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  network_configuration {
    egress_configuration {
      egress_type = "DEFAULT"
    }

    ingress_configuration {
      is_publicly_accessible = true
    }

    ip_address_type = "IPV4"
  }

  observability_configuration {
    observability_enabled           = true
    observability_configuration_arn = "arn:aws:apprunner:${var.aws_region}:${data.aws_caller_identity.current.account_id}:observabilityconfiguration/DefaultConfiguration/1/00000000000000000000000000000001"
  }


}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "assume_role_apprunner_access" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["build.apprunner.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "apprunner_access" {
  name               = "evalhub-apprunner-ecr-access-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_apprunner_access.json

  tags = {
    Name        = "evalhub-apprunner-ecr-access-role"
    Project     = "evalhub"
    ManagedBy   = "terraform"
    Environment = "production"
  }
}

resource "aws_iam_role_policy_attachment" "apprunner_access_ecr" {
  role       = aws_iam_role.apprunner_access.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

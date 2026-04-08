# Import existing App Runner service

resource "aws_apprunner_service" "evalhub" {
  service_name = var.apprunner_service_name

  source_configuration {
    authentication_configuration {
      connection_arn = var.apprunner_github_connection_arn
    }

    code_repository {
      repository_url   = var.apprunner_code_repository_url
      source_directory = "backend"

      code_configuration {
        configuration_source = "REPOSITORY"
      }

      source_code_version {
        type  = "BRANCH"
        value = var.apprunner_code_branch
      }
    }

    auto_deployments_enabled = false
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

  lifecycle {
    ignore_changes = [
      source_configuration[0].code_repository[0].source_code_version,
    ]
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

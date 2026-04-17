data "aws_iam_policy_document" "secrets_manager_read" {
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [
      for secret in aws_secretsmanager_secret.evalhub : secret.arn
    ]
  }
}

data "aws_iam_policy_document" "ecr_pull" {
  statement {
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage"
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "assume_role_apprunner" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["tasks.apprunner.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "assume_role_ec2" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "apprunner_instance" {
  name               = "evalhub-secrets-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_apprunner.json

  tags = {
    Name        = "evalhub-secrets-role"
    Project     = "evalhub"
    ManagedBy   = "terraform"
    Environment = "production"
  }
}

resource "aws_iam_policy" "secrets_manager_read" {
  name        = "evalhub-secrets-manager-read"
  description = "Allow reading evalhub secrets from Secrets Manager"
  policy      = data.aws_iam_policy_document.secrets_manager_read.json

  tags = {
    Name        = "evalhub-secrets-manager-read"
    Project     = "evalhub"
    ManagedBy   = "terraform"
    Environment = "production"
  }
}

resource "aws_iam_policy" "ecr_pull" {
  name        = "evalhub-ecr-pull"
  description = "Allow pulling images from ECR"
  policy      = data.aws_iam_policy_document.ecr_pull.json

  tags = {
    Name        = "evalhub-ecr-pull"
    Project     = "evalhub"
    ManagedBy   = "terraform"
    Environment = "production"
  }
}

resource "aws_iam_role_policy_attachment" "apprunner_secrets" {
  role       = aws_iam_role.apprunner_instance.name
  policy_arn = aws_iam_policy.secrets_manager_read.arn
}

resource "aws_iam_role_policy_attachment" "apprunner_ecr" {
  role       = aws_iam_role.apprunner_instance.name
  policy_arn = aws_iam_policy.ecr_pull.arn
}

resource "aws_iam_role" "ec2_instance" {
  name               = "evalhub-ec2-celery-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_ec2.json

  tags = {
    Name        = "evalhub-ec2-celery-role"
    Project     = "evalhub"
    ManagedBy   = "terraform"
    Environment = "production"
  }
}

resource "aws_iam_role_policy_attachment" "ec2_secrets" {
  role       = aws_iam_role.ec2_instance.name
  policy_arn = aws_iam_policy.secrets_manager_read.arn
}

resource "aws_iam_role_policy_attachment" "ec2_ecr" {
  role       = aws_iam_role.ec2_instance.name
  policy_arn = aws_iam_policy.ecr_pull.arn
}

resource "aws_iam_instance_profile" "ec2_celery" {
  name = "evalhub-ec2-celery-profile"
  role = aws_iam_role.ec2_instance.name

  tags = {
    Name        = "evalhub-ec2-celery-profile"
    Project     = "evalhub"
    ManagedBy   = "terraform"
    Environment = "production"
  }
}

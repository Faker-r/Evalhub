
output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.evalhub.id
}

output "kms_key_id" {
  description = "KMS key ID"
  value       = aws_kms_key.evalhub.id
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.celery_worker.id
}

output "ec2_public_dns" {
  description = "EC2 Celery worker public DNS"
  value       = aws_instance.celery_worker.public_dns
}

output "apprunner_service_url" {
  description = "App Runner service URL"
  value       = aws_apprunner_service.evalhub.service_url
}

output "secrets_arns" {
  description = "Map of secret names to their ARNs"
  value = {
    for key, secret in aws_secretsmanager_secret.evalhub : key => secret.arn
  }
  sensitive = true
}

output "ecr_repository_url" {
  description = "ECR repository URL for backend images"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_repository_arn" {
  description = "ECR repository ARN"
  value       = aws_ecr_repository.backend.arn
}

output "apprunner_instance_role_arn" {
  description = "App Runner instance role ARN"
  value       = aws_iam_role.apprunner_instance.arn
}

output "ec2_instance_profile_name" {
  description = "EC2 instance profile name for Celery workers"
  value       = aws_iam_instance_profile.ec2_celery.name
}

output "ec2_instance_role_arn" {
  description = "EC2 instance role ARN"
  value       = aws_iam_role.ec2_instance.arn
}

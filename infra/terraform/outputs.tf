output "vpc_id" {
  description = "VPC ID"
  value       = data.aws_vpc.existing.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = data.aws_vpc.existing.cidr_block
}

output "redis_endpoint" {
  description = "ElastiCache Serverless Redis endpoint"
  value       = aws_elasticache_serverless_cache.redis.endpoint[0].address
  sensitive   = true
}

output "redis_port" {
  description = "ElastiCache Serverless Redis port"
  value       = aws_elasticache_serverless_cache.redis.endpoint[0].port
}

output "redis_connection_string" {
  description = "Redis connection string for applications (with TLS)"
  value       = "rediss://${aws_elasticache_serverless_cache.redis.endpoint[0].address}:${aws_elasticache_serverless_cache.redis.endpoint[0].port}"
  sensitive   = true
}

output "apprunner_vpc_connector_arn" {
  description = "App Runner VPC Connector ARN"
  value       = aws_apprunner_vpc_connector.evalhub.arn
}

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

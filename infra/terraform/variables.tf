variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-2"
}


variable "default_tags" {
  description = "Default tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "Evalhub"
    ManagedBy   = "Terraform"
    Environment = "production"
  }
}

variable "s3_bucket_name" {
  description = "Name of the existing S3 bucket"
  type        = string
  default     = "evalhub-bucket"
}

variable "kms_key_id" {
  description = "KMS key ID for encryption"
  type        = string
  default     = "7b43a69b-9fe3-4239-beba-6c8bc4d2984e"
}

variable "ec2_instance_id" {
  description = "Existing EC2 instance ID for Celery workers"
  type        = string
  default     = "i-00c9fff40fd501441"
}

variable "apprunner_service_name" {
  description = "App Runner service name"
  type        = string
  default     = "evalhub-api-runner-github"
}

variable "certbot_email" {
  description = "Email address for Let's Encrypt certificate issuance and expiry notifications."
  type        = string
}



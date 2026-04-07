# ElastiCache Serverless Redis

# Security group for Redis
resource "aws_security_group" "redis" {
  name_prefix = "evalhub-redis-"
  description = "Security group for ElastiCache Serverless Redis"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Redis from App Runner VPC Connector"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.apprunner_connector.id]
  }

  ingress {
    description     = "Redis from EC2 Celery worker"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = ["sg-052807540561ab35a"]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "evalhub-redis"
  }
}

# Subnet group for ElastiCache
resource "aws_elasticache_subnet_group" "redis" {
  name       = "evalhub-redis-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name = "evalhub-redis"
  }
}

# ElastiCache Serverless cache
resource "aws_elasticache_serverless_cache" "redis" {
  engine = "redis"
  name   = var.elasticache_name

  cache_usage_limits {
    data_storage {
      maximum = var.elasticache_max_storage_gb
      unit    = "GB"
    }
    ecpu_per_second {
      maximum = var.elasticache_max_ecpu
    }
  }

  description              = "Evalhub Redis cache for Celery and application cache"
  major_engine_version     = "7"
  snapshot_retention_limit = 0
  security_group_ids       = [aws_security_group.redis.id]
  subnet_ids               = var.private_subnet_ids

  tags = {
    Name = "evalhub-redis"
  }
}

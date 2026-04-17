# Import existing EC2 instance

# Allow public inbound TLS connections to the HAProxy Redis proxy on port 6380.
# Port 6379 (plain Redis) is NOT opened; all external access goes through HAProxy.
resource "aws_security_group_rule" "ec2_redis_tls_inbound" {
  type              = "ingress"
  from_port         = 6380
  to_port           = 6380
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  ipv6_cidr_blocks  = ["::/0"]
  security_group_id = "sg-052807540561ab35a"
  description       = "Public Redis TLS via HAProxy (rediss://)"
}

resource "aws_instance" "celery_worker" {
  ami                  = "ami-0c55b159cbfafe1f0"
  instance_type        = "t3.medium"
  key_name             = "evalhub"
  subnet_id            = "subnet-027fa6ff0287a6478"
  iam_instance_profile = aws_iam_instance_profile.ec2_celery.name

  vpc_security_group_ids = ["sg-052807540561ab35a"]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  user_data = <<-EOF
    #!/bin/bash
    set -e
    
    yum update -y
    
    yum install -y docker git
    systemctl start docker
    systemctl enable docker
    usermod -a -G docker ec2-user
    
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    mkdir -p /opt/evalhub
    chown ec2-user:ec2-user /opt/evalhub
  EOF

  tags = {
    Name        = "evalhub-celery-worker"
    Project     = "evalhub"
    ManagedBy   = "terraform"
    Environment = "production"
    Role        = "celery-worker"
  }

  lifecycle {
    ignore_changes = [ami, user_data]
  }
}

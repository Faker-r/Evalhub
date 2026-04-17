# Elastic IP keeps the public address stable across stop/start so the cert and
# the client URL never change when the instance restarts.
resource "aws_eip" "celery_worker" {
  domain = "vpc"

  tags = {
    Name        = "evalhub-celery-eip"
    Project     = "evalhub"
    ManagedBy   = "terraform"
    Environment = "production"
  }
}

resource "aws_eip_association" "celery_worker" {
  instance_id   = aws_instance.celery_worker.id
  allocation_id = aws_eip.celery_worker.id
}

# sslip.io maps <a>-<b>-<c>-<d>.sslip.io → a.b.c.d with no setup required.
# Let's Encrypt issues certs for sslip.io names via HTTP-01 challenge.
locals {
  redis_hostname = "${replace(aws_eip.celery_worker.public_ip, ".", "-")}.sslip.io"
}

# Allow certbot HTTP-01 ACME challenges and renewals on port 80.
resource "aws_security_group_rule" "ec2_http_inbound" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  ipv6_cidr_blocks  = ["::/0"]
  security_group_id = "sg-052807540561ab35a"
  description       = "HTTP for certbot ACME HTTP-01 challenge"
}

# App Runner VPC Connector

# Security group for VPC connector
resource "aws_security_group" "apprunner_connector" {
  name_prefix = "evalhub-apprunner-connector-"
  description = "Security group for App Runner VPC connector"
  vpc_id      = var.vpc_id

  egress {
    description = "Allow all outbound to VPC"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [data.aws_vpc.existing.cidr_block]
  }

  tags = {
    Name = "evalhub-apprunner-connector"
  }
}

# VPC Connector for App Runner
resource "aws_apprunner_vpc_connector" "evalhub" {
  vpc_connector_name = "evalhub-vpc-connector"
  subnets            = var.private_subnet_ids
  security_groups    = [aws_security_group.apprunner_connector.id]

  tags = {
    Name = "evalhub-vpc-connector"
  }
}

# Import existing App Runner service

resource "aws_apprunner_service" "evalhub" {
  service_name = var.apprunner_service_name

  source_configuration {
    authentication_configuration {
      connection_arn = "arn:aws:apprunner:us-east-2:214863335048:connection/AWS-Github-Evalhub/9de71d8c50f74f0bb15f460eaae99a3d"
    }

    code_repository {
      repository_url = "https://github.com/Faker-r/Evalhub"

      source_code_version {
        type  = "BRANCH"
        value = "apprunner-python311"
      }

      code_configuration {
        configuration_source = "REPOSITORY"
      }

      source_directory = "backend"
    }

    auto_deployments_enabled = false
  }

  instance_configuration {
    cpu               = "1024"
    memory            = "2048"
    instance_role_arn = "arn:aws:iam::214863335048:role/evalhub-secrets-role"
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
      egress_type       = "VPC"
      vpc_connector_arn = aws_apprunner_vpc_connector.evalhub.arn
    }

    ingress_configuration {
      is_publicly_accessible = true
    }

    ip_address_type = "IPV4"
  }

  observability_configuration {
    observability_enabled         = true
    observability_configuration_arn = "arn:aws:apprunner:us-east-2:214863335048:observabilityconfiguration/DefaultConfiguration/1/00000000000000000000000000000001"
  }

  lifecycle {
    ignore_changes = [
      source_configuration[0].code_repository[0].source_code_version[0].value,
    ]
  }
}

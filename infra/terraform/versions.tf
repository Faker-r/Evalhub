terraform {
  required_version = ">= 1.9.0"

  backend "s3" {
    bucket         = "evalhub-terraform-state"
    key            = "evalhub/terraform.tfstate"
    region         = "us-east-2"
    dynamodb_table = "evalhub-terraform-locks"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

terraform {
  required_version = "~> 1.16"

  required_providers {
    # The VPC module (>= 6.28) and the EKS module (>= 6.59) both need AWS provider 6.
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.69"
    }
  }
}

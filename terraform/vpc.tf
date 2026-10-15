# Network: 2 public subnets, 2 private subnets and one shared NAT gateway.
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.8"

  name = "${var.project}-vpc"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  public_subnets  = var.public_subnet_cidrs
  private_subnets = var.private_subnet_cidrs

  # one NAT gateway for the whole VPC keeps the cost down
  enable_nat_gateway = true
  single_nat_gateway = true

  # instances started in a public subnet get a public address
  map_public_ip_on_launch = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  # these tags let Kubernetes place load balancers in the right subnets
  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }

  tags = local.tags
}

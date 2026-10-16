# Everything IronPass needs on AWS: a VPC, an EKS cluster with worker nodes,
# and the IAM pieces that let GitHub Actions deploy without stored keys.

provider "aws" {
  region = var.aws_region

  # every resource that supports tags gets these automatically
  default_tags {
    tags = local.tags
  }
}

locals {
  tags = {
    Project     = var.project
    ManagedBy   = "terraform"
    Environment = var.environment
  }
}

# ---------------------------------------------------------------------------
# Availability zones are looked up, not typed in, so changing the region works.
# ---------------------------------------------------------------------------
data "aws_availability_zones" "available" {
  state = "available"

  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

locals {
  # the first two zones of the region
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

# ---------------------------------------------------------------------------
# Network: 2 public subnets, 2 private subnets and one shared NAT gateway.
# ---------------------------------------------------------------------------
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.7"

  name = "${var.project}-vpc"
  cidr = var.vpc_cidr

  azs             = local.azs
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

# ---------------------------------------------------------------------------
# EKS control plane and one managed node group.
# ---------------------------------------------------------------------------
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.29"

  name               = var.cluster_name
  kubernetes_version = var.kubernetes_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  endpoint_public_access = true

  # keep the demo small: no extra KMS key and no control plane log group,
  # both would stay behind after destroy and cost money
  create_kms_key              = false
  encryption_config           = null
  create_cloudwatch_log_group = false
  enabled_log_types           = []

  # the person running terraform becomes cluster admin
  enable_cluster_creator_admin_permissions = true

  addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent    = true
      before_compute = true
    }
    # needed so the postgres PersistentVolumeClaim can create an EBS volume
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  eks_managed_node_groups = {
    main = {
      ami_type = "AL2023_x86_64_STANDARD"

      # t3.medium is the usual choice, but this AWS account is on the free plan
      # and it refuses t3.medium ("not eligible for Free Tier"). c7i-flex.large
      # has the same size (2 vCPU, 4 GiB) and is allowed. Do not switch back.
      instance_types = [var.node_instance_type]

      min_size     = var.node_min_size
      max_size     = var.node_max_size
      desired_size = var.node_desired_size

      iam_role_additional_policies = {
        ebs_csi = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
      }

      # The cluster was built with module v20, which used these two settings.
      # Module v21 changed the defaults, and that would replace every node.
      # Pods (the EBS CSI driver) need hop limit 2 to reach the node role.
      enable_monitoring = true

      metadata_options = {
        http_endpoint               = "enabled"
        http_tokens                 = "required"
        http_put_response_hop_limit = 2
      }
    }
  }

  tags = local.tags
}

# ---------------------------------------------------------------------------
# GitHub Actions signs in to AWS with a short lived token, so no access keys
# are stored in GitHub.
# ---------------------------------------------------------------------------
resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]

  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
  ]
}

data "aws_iam_policy_document" "github_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # only the main branch of this one repository
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["${var.github_oidc_subject_prefix}:ref:refs/heads/${var.github_branch}"]
    }
  }
}

resource "aws_iam_role" "github_deploy" {
  name               = "${var.project}-github-deploy"
  description        = "Assumed by GitHub Actions to deploy IronPass to EKS"
  assume_role_policy = data.aws_iam_policy_document.github_assume_role.json
}

# The role may only read this one cluster so it can build a kubeconfig.
data "aws_iam_policy_document" "describe_cluster" {
  statement {
    effect    = "Allow"
    actions   = ["eks:DescribeCluster"]
    resources = [module.eks.cluster_arn]
  }
}

resource "aws_iam_role_policy" "describe_cluster" {
  name   = "describe-ironpass-cluster"
  role   = aws_iam_role.github_deploy.id
  policy = data.aws_iam_policy_document.describe_cluster.json
}

# Inside the cluster the role is limited to the application namespace.
resource "aws_eks_access_entry" "github_deploy" {
  cluster_name  = module.eks.cluster_name
  principal_arn = aws_iam_role.github_deploy.arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "github_deploy" {
  cluster_name  = module.eks.cluster_name
  principal_arn = aws_iam_role.github_deploy.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type       = "namespace"
    namespaces = [var.app_namespace]
  }

  depends_on = [aws_eks_access_entry.github_deploy]
}

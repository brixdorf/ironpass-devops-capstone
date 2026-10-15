# GitHub Actions signs in to AWS with a short lived token, so no access keys
# are stored in GitHub.

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

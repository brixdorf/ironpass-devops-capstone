output "region" {
  description = "AWS region"
  value       = var.aws_region
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.vpc.public_subnets
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.vpc.private_subnets
}

output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "API server endpoint of the EKS cluster"
  value       = module.eks.cluster_endpoint
}

output "configure_kubectl" {
  description = "Command that writes the kubeconfig entry for this cluster"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

output "github_deploy_role_arn" {
  description = "IAM role that GitHub Actions assumes (set it as the AWS_ROLE_ARN repository variable)"
  value       = aws_iam_role.github_deploy.arn
}

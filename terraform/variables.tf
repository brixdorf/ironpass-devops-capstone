variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-south-1"
}

variable "project" {
  description = "Project name, used in resource names and tags"
  type        = string
  default     = "ironpass"
}

variable "environment" {
  description = "Environment name used in tags"
  type        = string
  default     = "dev"
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "ironpass-eks"
}

variable "kubernetes_version" {
  description = "Kubernetes version for the EKS control plane"
  type        = string
  default     = "1.35"
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "availability_zones" {
  description = "Two availability zones, one public and one private subnet in each"
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks of the two public subnets"
  type        = list(string)
  default     = ["10.20.101.0/24", "10.20.102.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks of the two private subnets"
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
}

variable "node_instance_type" {
  description = "EC2 instance type of the worker nodes. This AWS account is on the free plan, which refuses t3.medium, so the default is c7i-flex.large (same 2 vCPU and 4 GiB)."
  type        = string
  default     = "c7i-flex.large"
}

variable "node_desired_size" {
  description = "Number of worker nodes to run normally"
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Smallest number of worker nodes"
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Largest number of worker nodes"
  type        = number
  default     = 3
}

variable "app_namespace" {
  description = "Kubernetes namespace the pipeline is allowed to deploy into"
  type        = string
  default     = "ironpass"
}

variable "github_repository" {
  description = "GitHub repository allowed to deploy, in the form owner/name"
  type        = string
  default     = "brixdorf/ironpass-devops-capstone"
}

variable "github_oidc_subject_prefix" {
  description = "Start of the OIDC subject that GitHub puts in its tokens. New repositories use ids, for example repo:owner@123/name@456. Find it with: gh api repos/OWNER/NAME/actions/oidc/customization/sub"
  type        = string
  default     = "repo:brixdorf@180433577/ironpass-devops-capstone@1421043713"
}

variable "github_branch" {
  description = "Only this branch of the repository can assume the deploy role"
  type        = string
  default     = "main"
}

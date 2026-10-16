# Terraform

Creates the AWS side of IronPass in `ap-south-1`. The availability zones are looked up with a data source, so changing `aws_region` works.

| File | What it makes |
| --- | --- |
| `versions.tf` | Terraform and AWS provider versions |
| `main.tf` | availability zone lookup, VPC (2 public and 2 private subnets, one NAT gateway), EKS cluster with a managed node group and add-ons, GitHub OIDC provider, deploy role and EKS access entry |
| `variables.tf` | every input with a description and a default |
| `outputs.tf` | cluster name, endpoint, subnet ids and the role ARN |
| `terraform.tfvars.example` | sample values, copy it to `terraform.tfvars` |

Every resource is tagged `Project=ironpass` and `ManagedBy=terraform`.

## Use it

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # optional
terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply
aws eks update-kubeconfig --region ap-south-1 --name ironpass-eks
```

Then run `scripts/bootstrap-cluster.sh` and `scripts/install-monitoring.sh` from the repo root.

## Notes

- The state file stays on local disk (`terraform.tfstate`, ignored by git). Keep a copy outside the repo.
- The AWS account used for this project is on the free plan and refuses `t3.medium`. The nodes are `c7i-flex.large`, which has the same 2 vCPU and 4 GiB. On a normal account set `node_instance_type = "t3.medium"`.
- GitHub now puts repository ids in the OIDC subject. `github_oidc_subject_prefix` holds that value. Find yours with `gh api repos/OWNER/NAME/actions/oidc/customization/sub`.
- To remove everything use `scripts/teardown.sh`, not a bare `terraform destroy`, because the load balancer is created by Kubernetes and blocks the VPC delete.

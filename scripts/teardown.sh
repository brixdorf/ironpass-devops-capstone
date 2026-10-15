#!/usr/bin/env bash
# Removes everything IronPass created on AWS.
#
# Order matters. The load balancer is created by Kubernetes, not by Terraform.
# If it is still there, the VPC cannot be deleted. So the Helm releases go
# first, then terraform destroy, then a check that nothing is left.
#
# Usage:
#   ./scripts/teardown.sh --dry-run   show what would run, change nothing
#   ./scripts/teardown.sh --yes       really tear everything down
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REGION="${AWS_REGION:-ap-south-1}"
CLUSTER="${CLUSTER_NAME:-ironpass-eks}"
DRY_RUN=1

case "${1:-}" in
  --yes) DRY_RUN=0 ;;
  --dry-run | "") DRY_RUN=1 ;;
  *) echo "Usage: $0 [--dry-run | --yes]"; exit 2 ;;
esac

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] $*"
  else
    echo "+ $*"
    "$@"
  fi
}

# helm uninstall that does not fail when the release is already gone
uninstall() {
  local release="$1" namespace="$2"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "[dry-run] helm uninstall $release -n $namespace --wait"
  elif helm status "$release" -n "$namespace" >/dev/null 2>&1; then
    echo "+ helm uninstall $release -n $namespace"
    helm uninstall "$release" -n "$namespace" --wait
  else
    echo "release $release not found in $namespace, skipping"
  fi
}

echo "== 1. remove workloads, so volumes and load balancers are released"
if [ "$DRY_RUN" -eq 0 ]; then
  aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER" >/dev/null
fi
run kubectl delete -f "$ROOT/troubleshooting/" --ignore-not-found
uninstall ironpass ironpass
uninstall kube-prometheus-stack monitoring
uninstall ingress-nginx ingress-nginx
uninstall metrics-server kube-system
run kubectl delete pvc --all -n ironpass --ignore-not-found
run kubectl delete pvc --all -n monitoring --ignore-not-found

echo "== 2. wait until the load balancers are gone"
if [ "$DRY_RUN" -eq 1 ]; then
  echo "[dry-run] poll elb and elbv2 for load balancers tagged Project=ironpass"
else
  for _ in $(seq 1 30); do
    left=$(aws resourcegroupstaggingapi get-resources --region "$REGION" \
      --tag-filters Key=Project,Values=ironpass \
      --resource-type-filters elasticloadbalancing:loadbalancer elasticloadbalancing \
      --query 'length(ResourceTagMappingList)' --output text)
    [ "$left" = "0" ] && break
    echo "still $left load balancer(s), waiting"
    sleep 10
  done
fi

echo "== 3. terraform destroy"
if [ "$DRY_RUN" -eq 1 ]; then
  echo "[dry-run] terraform -chdir=$ROOT/terraform destroy -auto-approve"
else
  terraform -chdir="$ROOT/terraform" destroy -auto-approve
fi

echo "== 4. verify nothing is left"
if [ "$DRY_RUN" -eq 1 ]; then
  echo "[dry-run] terraform state list must be empty"
  echo "[dry-run] resourcegroupstaggingapi get-resources --tag-filters Project=ironpass must be empty"
  echo "[dry-run] check elb, elbv2, ebs volumes, nat gateways, network interfaces, eks clusters"
  exit 0
fi

failed=0

state=$(terraform -chdir="$ROOT/terraform" state list 2>/dev/null || true)
if [ -n "$state" ]; then
  echo "FAIL terraform state is not empty:"; echo "$state"; failed=1
else
  echo "ok   terraform state is empty"
fi

tagged=$(aws resourcegroupstaggingapi get-resources --region "$REGION" \
  --tag-filters Key=Project,Values=ironpass \
  --query 'ResourceTagMappingList[].ResourceARN' --output text)
if [ -n "$tagged" ]; then
  echo "FAIL resources still tagged Project=ironpass:"; echo "$tagged"; failed=1
else
  echo "ok   no resources tagged Project=ironpass"
fi

check() {
  local label="$1" value="$2"
  if [ -n "$value" ] && [ "$value" != "None" ]; then
    echo "FAIL $label left: $value"; failed=1
  else
    echo "ok   no $label"
  fi
}

# classic load balancers carry the tag we set in k8s/ingress-nginx-values.yaml
elb_names=$(aws elb describe-load-balancers --region "$REGION" \
  --query 'LoadBalancerDescriptions[].LoadBalancerName' --output text | tr '\t' ' ')
elb_left=""
for name in $elb_names; do
  hit=$(aws elb describe-tags --region "$REGION" --load-balancer-names "$name" \
    --query "TagDescriptions[].Tags[?Key=='Project' && Value=='ironpass'] | [0][0].Value" --output text)
  [ "$hit" = "ironpass" ] && elb_left="$elb_left $name"
done
check "classic load balancers" "$elb_left"
check "network load balancers" "$(aws elbv2 describe-load-balancers --region "$REGION" \
  --query "LoadBalancers[?contains(LoadBalancerName, 'ironpass')].LoadBalancerArn" --output text)"
check "ebs volumes" "$(aws ec2 describe-volumes --region "$REGION" \
  --filters Name=tag:Project,Values=ironpass --query 'Volumes[].VolumeId' --output text)"
check "ebs volumes from the csi driver" "$(aws ec2 describe-volumes --region "$REGION" \
  --filters Name=tag-key,Values=kubernetes.io/created-for/pvc/name Name=tag:kubernetes.io/cluster/$CLUSTER,Values=owned \
  --query 'Volumes[].VolumeId' --output text)"
check "nat gateways" "$(aws ec2 describe-nat-gateways --region "$REGION" \
  --filter Name=tag:Project,Values=ironpass Name=state,Values=pending,available \
  --query 'NatGateways[].NatGatewayId' --output text)"
check "network interfaces" "$(aws ec2 describe-network-interfaces --region "$REGION" \
  --filters Name=tag:Project,Values=ironpass --query 'NetworkInterfaces[].NetworkInterfaceId' --output text)"
check "eks cluster" "$(aws eks list-clusters --region "$REGION" \
  --query "clusters[?contains(@, 'ironpass')]" --output text)"

if [ "$failed" -ne 0 ]; then
  echo "Teardown finished with leftovers, see FAIL lines above."
  exit 1
fi
echo "Teardown complete. Nothing tagged Project=ironpass is left."

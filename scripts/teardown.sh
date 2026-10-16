#!/usr/bin/env bash
# Removes everything IronPass created on AWS, in the order that works.
#
# Why the order matters: the load balancer and the database volumes are created
# by Kubernetes, not by Terraform. If they are still there, the VPC cannot be
# deleted and terraform destroy hangs. So the workloads go first.
#
#   1. turn the pipeline deploy switch off (DEPLOY_ENABLED=false)
#   2. uninstall the Helm releases: ironpass, kube-prometheus-stack, traefik, metrics-server
#   3. delete the PVCs and wait until the EBS volumes are gone
#   4. wait until the load balancer is gone
#   5. terraform destroy (output is saved to docs/terraform-destroy-output.txt)
#   6. check that nothing tagged Project=ironpass is left
#   7. remove the stale GitHub repository variables
#
# Usage:
#   ./scripts/teardown.sh --dry-run   show what would run, change nothing (default)
#   ./scripts/teardown.sh --verify    only run the checks of step 6, change nothing
#   ./scripts/teardown.sh --yes       really tear everything down
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REGION="${AWS_REGION:-ap-south-1}"
CLUSTER="${CLUSTER_NAME:-ironpass-eks}"
ROLE_NAME="${ROLE_NAME:-ironpass-github-deploy}"
DESTROY_LOG="$ROOT/docs/terraform-destroy-output.txt"
WAIT_MINUTES="${WAIT_MINUTES:-15}"      # per waiting step
DESTROY_MINUTES="${DESTROY_MINUTES:-45}" # for terraform destroy
export AWS_PAGER=""

MODE="dry-run"
case "${1:-}" in
  --yes) MODE="run" ;;
  --verify) MODE="verify" ;;
  --dry-run | "") MODE="dry-run" ;;
  *) echo "Usage: $0 [--dry-run | --verify | --yes]"; exit 2 ;;
esac

say() { echo; echo "== $*"; }

run() {
  if [ "$MODE" = "dry-run" ]; then
    echo "[dry-run] $*"
  else
    echo "+ $*"
    "$@"
  fi
}

# Waits until the command succeeds. Stops with a clear message after WAIT_MINUTES.
wait_for() {
  local what="$1"; shift
  if [ "$MODE" = "dry-run" ]; then
    echo "[dry-run] wait up to ${WAIT_MINUTES} minutes until $what"
    return 0
  fi
  local end=$((SECONDS + WAIT_MINUTES * 60))
  until "$@"; do
    if [ "$SECONDS" -ge "$end" ]; then
      echo "TIMEOUT: $what is still not true after ${WAIT_MINUTES} minutes."
      echo "Look in the AWS console (EC2, Load Balancers and Volumes) for what is stuck,"
      echo "remove it, then run this script again. It is safe to run twice."
      exit 1
    fi
    echo "waiting: $what"
    sleep 10
  done
  echo "done: $what"
}

# ---- AWS credentials for terraform -----------------------------------------
# With "aws login" sessions terraform cannot read the credentials by itself.
# This lets the aws CLI hand them over on demand. Nothing is printed or stored.
TF_PREFIX=()
TF_CFG=""
setup_terraform_credentials() {
  [ -n "${AWS_ACCESS_KEY_ID:-}" ] && return 0
  command -v aws >/dev/null 2>&1 || return 0
  aws configure export-credentials --format process >/dev/null 2>&1 || return 0
  TF_CFG="$(mktemp)"
  trap 'rm -f "$TF_CFG"' EXIT
  cat > "$TF_CFG" <<CFG
[profile ironpass-terraform]
credential_process = env AWS_CONFIG_FILE=${AWS_CONFIG_FILE:-$HOME/.aws/config} $(command -v aws) configure export-credentials --profile ${AWS_PROFILE:-default} --format process
region = $REGION
CFG
  TF_PREFIX=(env "AWS_CONFIG_FILE=$TF_CFG" AWS_PROFILE=ironpass-terraform)
}

terraform_cmd() {
  "${TF_PREFIX[@]}" terraform -chdir="$ROOT/terraform" "$@"
}

# helm uninstall that does not fail when the release is already gone
uninstall() {
  local release="$1" namespace="$2"
  if [ "$MODE" = "dry-run" ]; then
    echo "[dry-run] helm uninstall $release -n $namespace --wait --timeout ${WAIT_MINUTES}m"
  elif helm status "$release" -n "$namespace" >/dev/null 2>&1; then
    echo "+ helm uninstall $release -n $namespace"
    helm uninstall "$release" -n "$namespace" --wait --timeout "${WAIT_MINUTES}m"
  else
    echo "release $release not found in $namespace, skipping"
  fi
}

# ---- waiting conditions ----------------------------------------------------
no_pvc_volumes_left() {
  [ -z "$(aws ec2 describe-volumes --region "$REGION" \
    --filters "Name=tag-key,Values=kubernetes.io/created-for/pvc/name" \
              "Name=tag:kubernetes.io/cluster/$CLUSTER,Values=owned" \
    --query 'Volumes[].VolumeId' --output text)" ]
}

classic_lbs_left() {
  local name hit
  for name in $(aws elb describe-load-balancers --region "$REGION" \
      --query 'LoadBalancerDescriptions[].LoadBalancerName' --output text); do
    hit=$(aws elb describe-tags --region "$REGION" --load-balancer-names "$name" \
      --query "TagDescriptions[].Tags[?Key=='Project' && Value=='ironpass'] | [0][0].Value" --output text)
    [ "$hit" = "ironpass" ] && printf '%s ' "$name"
  done
  return 0
}

no_load_balancer_left() {
  [ -z "$(classic_lbs_left)" ] && \
  [ -z "$(aws elbv2 describe-load-balancers --region "$REGION" \
    --query "LoadBalancers[?contains(LoadBalancerName, 'ironpass')].LoadBalancerArn" --output text)" ]
}

# ---- step 6: the final checks ----------------------------------------------
verify_nothing_left() {
  local failed=0
  check() {
    local label="$1" value="$2"
    if [ -n "$value" ] && [ "$value" != "None" ]; then
      echo "FAIL $label left: $value"; failed=1
    else
      echo "ok   no $label"
    fi
  }

  local state
  state=$(terraform_cmd state list 2>/dev/null || true)
  if [ -n "$state" ]; then
    echo "FAIL terraform state is not empty ($(echo "$state" | wc -l) resources)"; failed=1
  else
    echo "ok   terraform state is empty"
  fi

  check "resources tagged Project=ironpass" "$(aws resourcegroupstaggingapi get-resources --region "$REGION" \
    --tag-filters Key=Project,Values=ironpass --query 'ResourceTagMappingList[].ResourceARN' --output text)"
  check "classic load balancers" "$(classic_lbs_left)"
  check "application or network load balancers" "$(aws elbv2 describe-load-balancers --region "$REGION" \
    --query "LoadBalancers[?contains(LoadBalancerName, 'ironpass')].LoadBalancerArn" --output text)"
  check "ebs volumes tagged Project=ironpass" "$(aws ec2 describe-volumes --region "$REGION" \
    --filters Name=tag:Project,Values=ironpass --query 'Volumes[].VolumeId' --output text)"
  check "ebs volumes from the csi driver" "$(aws ec2 describe-volumes --region "$REGION" \
    --filters "Name=tag-key,Values=kubernetes.io/created-for/pvc/name" \
              "Name=tag:kubernetes.io/cluster/$CLUSTER,Values=owned" \
    --query 'Volumes[].VolumeId' --output text)"
  check "nat gateways" "$(aws ec2 describe-nat-gateways --region "$REGION" \
    --filter Name=tag:Project,Values=ironpass Name=state,Values=pending,available \
    --query 'NatGateways[].NatGatewayId' --output text)"
  check "network interfaces" "$(aws ec2 describe-network-interfaces --region "$REGION" \
    --filters Name=tag:Project,Values=ironpass --query 'NetworkInterfaces[].NetworkInterfaceId' --output text)"
  check "eks clusters" "$(aws eks list-clusters --region "$REGION" \
    --query "clusters[?contains(@, 'ironpass')]" --output text)"
  check "github oidc provider" "$(aws iam list-open-id-connect-providers \
    --query "OpenIDConnectProviderList[?contains(Arn, 'token.actions.githubusercontent.com')].Arn" --output text)"
  check "iam role $ROLE_NAME" "$(aws iam list-roles \
    --query "Roles[?RoleName=='$ROLE_NAME'].Arn" --output text)"

  return "$failed"
}

# ---- go --------------------------------------------------------------------
setup_terraform_credentials

if [ "$MODE" = "verify" ]; then
  say "checks only (nothing is changed)"
  verify_nothing_left || { echo "Leftovers found, see FAIL lines above."; exit 1; }
  echo "Nothing tagged Project=ironpass is left."
  exit 0
fi

if [ "$MODE" = "run" ]; then
  aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER" >/dev/null
fi

say "1. turn the pipeline deploy switch off"
run gh variable set DEPLOY_ENABLED --body false

say "2. uninstall the Helm releases (the load balancer is removed with traefik)"
run kubectl delete -f "$ROOT/troubleshooting/" --ignore-not-found
uninstall ironpass ironpass
uninstall kube-prometheus-stack monitoring
uninstall traefik traefik
uninstall metrics-server kube-system

say "3. delete the PVCs and wait until the EBS volumes are gone"
run kubectl delete pvc --all -n ironpass --ignore-not-found
run kubectl delete pvc --all -n monitoring --ignore-not-found
wait_for "no EBS volumes created for PVCs of $CLUSTER" no_pvc_volumes_left

say "4. wait until the load balancer is gone"
wait_for "no ironpass load balancer exists" no_load_balancer_left

say "5. terraform destroy (output is also saved to docs/terraform-destroy-output.txt)"
if [ "$MODE" = "dry-run" ]; then
  echo "[dry-run] timeout ${DESTROY_MINUTES}m terraform -chdir=terraform destroy -auto-approve -no-color | tee $DESTROY_LOG"
else
  if ! timeout "${DESTROY_MINUTES}m" "${TF_PREFIX[@]}" terraform -chdir="$ROOT/terraform" destroy -auto-approve -no-color 2>&1 | tee "$DESTROY_LOG"; then
    echo "TIMEOUT or error: terraform destroy did not finish within ${DESTROY_MINUTES} minutes."
    echo "Run 'terraform -chdir=terraform destroy' again, it continues where it stopped."
    exit 1
  fi
fi

say "6. verify nothing is left"
if [ "$MODE" = "dry-run" ]; then
  echo "[dry-run] terraform state list must be empty"
  echo "[dry-run] no resources tagged Project=ironpass"
  echo "[dry-run] no load balancers, ebs volumes, nat gateways, network interfaces, eks clusters"
  echo "[dry-run] no github oidc provider and no iam role $ROLE_NAME"
else
  verify_nothing_left || { echo "Teardown finished with leftovers, see FAIL lines above."; exit 1; }
fi

say "7. remove the stale GitHub repository variables"
for var in AWS_ROLE_ARN AWS_REGION EKS_CLUSTER_NAME; do
  run gh variable delete "$var"
done

if [ "$MODE" = "run" ]; then
  echo
  echo "Teardown complete. Nothing tagged Project=ironpass is left."
  echo "Next: add the teardown date to README.md and commit docs/terraform-destroy-output.txt."
fi

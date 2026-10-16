#!/usr/bin/env bash
# Installs Prometheus and Grafana and loads the IronPass dashboard.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --version 92.9.0 \
  -f "$ROOT/monitoring/kube-prometheus-stack-values.yaml" \
  --wait --timeout 10m

# The Grafana sidecar picks up any ConfigMap labelled grafana_dashboard=1.
kubectl create configmap ironpass-dashboard \
  --namespace monitoring \
  --from-file=ironpass.json="$ROOT/monitoring/dashboards/ironpass.json" \
  --dry-run=client -o yaml \
  | kubectl label --local -f - grafana_dashboard=1 -o yaml \
  | kubectl apply -f -

kubectl get pods -n monitoring

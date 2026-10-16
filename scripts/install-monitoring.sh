#!/usr/bin/env bash
# Installs Prometheus and Grafana (kube-prometheus-stack).
# The IronPass dashboard and the ServiceMonitor come with the app's Helm chart,
# so they appear as soon as the app is deployed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --version 92.9.0 \
  -f "$ROOT/monitoring/kube-prometheus-stack-values.yaml" \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set-json 'prometheus.prometheusSpec.serviceMonitorNamespaceSelector={}' \
  --wait --timeout 10m

kubectl get pods -n monitoring

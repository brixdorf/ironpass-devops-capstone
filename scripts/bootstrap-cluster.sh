#!/usr/bin/env bash
# One time setup of the cluster add-ons that the app needs:
# namespace, storage class, ingress-nginx and metrics-server.
# Run it after terraform apply and after the kubeconfig is in place.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "== namespace and storage class"
kubectl apply -f "$ROOT/k8s/namespace.yaml"
kubectl apply -f "$ROOT/k8s/storageclass-gp3.yaml"

echo "== helm repositories"
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update

echo "== ingress-nginx"
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --version 4.15.1 \
  -f "$ROOT/k8s/ingress-nginx-values.yaml" \
  --wait --timeout 5m

echo "== metrics-server"
helm upgrade --install metrics-server metrics-server/metrics-server \
  --namespace kube-system \
  --version 3.14.0 \
  --wait --timeout 5m

echo "== load balancer address"
kubectl get svc -n ingress-nginx ingress-nginx-controller

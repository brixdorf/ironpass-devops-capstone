#!/usr/bin/env bash
# Smoke test on a throwaway cluster (kind in the pipeline, or on your laptop).
# It needs the images ironpass-backend:ci and ironpass-frontend:ci inside the
# cluster. On kind load them first:
#   kind load docker-image ironpass-backend:ci ironpass-frontend:ci
#
# It applies the plain manifests in k8s/, waits for every pod, then calls the
# app through a port-forward: /health, /ready and the /api paths.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NS=ironpass
PF_PID=""

cleanup() { [ -n "$PF_PID" ] && kill "$PF_PID" 2>/dev/null || true; }
trap cleanup EXIT

dump_logs() {
  echo "---- smoke test failed, cluster state ----"
  kubectl get pods -n "$NS" -o wide || true
  kubectl describe pods -n "$NS" | tail -60 || true
  kubectl logs -n "$NS" deploy/backend --tail=60 || true
}

kubectl apply -f "$ROOT/k8s/namespace.yaml"

# random password, created here so it never sits in git
kubectl create secret generic ironpass-db -n "$NS" \
  --from-literal=POSTGRES_PASSWORD="$(head -c 18 /dev/urandom | base64 | tr -dc 'A-Za-z0-9')" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f "$ROOT/k8s/postgres.yaml"
kubectl rollout status deployment/postgres -n "$NS" --timeout=180s || { dump_logs; exit 1; }

kubectl apply -f "$ROOT/k8s/backend.yaml"
kubectl apply -f "$ROOT/k8s/frontend.yaml"
for d in backend frontend; do
  kubectl rollout status "deployment/$d" -n "$NS" --timeout=180s || { dump_logs; exit 1; }
done
kubectl wait --for=condition=Ready pod --all -n "$NS" --timeout=60s || { dump_logs; exit 1; }
kubectl get pods,svc -n "$NS"

check() {
  local url="$1" expect="$2" body
  for _ in $(seq 1 15); do
    body="$(curl -fsS "$url" 2>/dev/null || true)"
    if echo "$body" | grep -q "$expect"; then
      echo "ok   $url contains $expect"
      return 0
    fi
    sleep 2
  done
  echo "FAIL $url did not contain $expect, got: $body"
  dump_logs
  exit 1
}

kubectl port-forward -n "$NS" svc/backend 18000:8000 >/dev/null 2>&1 &
PF_PID=$!
sleep 3
check http://127.0.0.1:18000/health '"status":"ok"'
check http://127.0.0.1:18000/ready '"status":"ready"'
check http://127.0.0.1:18000/api/plans 'MONTHLY'
check http://127.0.0.1:18000/api/stats 'total_members'
kill "$PF_PID"; PF_PID=""

# the same API again, now through the frontend (nginx forwards /api to the backend)
kubectl port-forward -n "$NS" svc/frontend 18080:80 >/dev/null 2>&1 &
PF_PID=$!
sleep 3
check http://127.0.0.1:18080/health 'ok'
check http://127.0.0.1:18080/api/members 'full_name'
check http://127.0.0.1:18080/ 'root'

echo "Smoke test passed"

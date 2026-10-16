#!/usr/bin/env bash
# Reads the numbers used in the "At a glance" row of the README from the real project.
# Needs: backend/.venv, gh (logged in), kubectl pointing at the cluster, and
#   kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090
set -euo pipefail
cd "$(dirname "$0")/../../.."

endpoints=$(cd backend && DATABASE_URL=sqlite:// .venv/bin/python -c "
from app.main import app
print(sum(len([m for m in item if m in ('get','post','put','delete','patch')]) for path, item in app.openapi()['paths'].items() if path != '/'))")
tests=$(cd backend && .venv/bin/pytest --collect-only -q 2>/dev/null | grep -c '::')
pipeline=$(gh run list --workflow ci-cd.yml --status success --limit 1 --json createdAt,updatedAt \
  --jq '((.[0].updatedAt|fromdate) - (.[0].createdAt|fromdate))')
pods=$(kubectl get pods -n ironpass --no-headers | wc -l)
targets=$(curl -s 'http://localhost:9090/api/v1/query?query=count(up==1)' | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['result'][0]['value'][1])")

echo "endpoints=$endpoints"
echo "tests=$tests"
echo "pipeline_seconds=$pipeline"
echo "pods=$pods"
echo "prometheus_targets_up=$targets"

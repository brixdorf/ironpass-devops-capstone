#!/usr/bin/env bash
# Sends steady traffic to the API so the backend CPU goes up and the HPA
# adds pods. Watch it in a second terminal with:
#   kubectl get hpa -n ironpass -w
#
# Usage: URL=http://<ingress-hostname> ./scripts/load-test.sh
set -euo pipefail

URL="${URL:?set URL, for example URL=http://my-elb.ap-south-1.elb.amazonaws.com}"
DURATION="${DURATION:-240}"        # seconds
CONCURRENCY="${CONCURRENCY:-30}"   # parallel clients
NAMESPACE="${NAMESPACE:-ironpass}"

echo "Sending traffic to $URL for ${DURATION}s with $CONCURRENCY clients"

worker() {
  local end=$((SECONDS + DURATION))
  while [ "$SECONDS" -lt "$end" ]; do
    # these endpoints all hit the database, so they cost real CPU
    curl -s -o /dev/null "$URL/api/members"
    curl -s -o /dev/null "$URL/api/stats"
    curl -s -o /dev/null "$URL/api/checkins?limit=50"
  done
}

for _ in $(seq 1 "$CONCURRENCY"); do
  worker &
done

# print the autoscaler state while the load runs
if command -v kubectl >/dev/null 2>&1; then
  end=$((SECONDS + DURATION))
  while [ "$SECONDS" -lt "$end" ]; do
    kubectl get hpa -n "$NAMESPACE" --no-headers 2>/dev/null | sed "s/^/[$(date +%H:%M:%S)] /" || true
    sleep 15
  done
fi

wait
echo "Load test finished"

# Monitoring

Prometheus collects the numbers, Grafana draws them.

| Piece | Where it is defined |
| --- | --- |
| Prometheus and Grafana | `kube-prometheus-stack-values.yaml` (this folder) |
| ServiceMonitor, tells Prometheus to scrape the backend `/metrics` | `helm/ironpass/templates/servicemonitor.yaml` |
| Grafana dashboard as code (request rate, latency, error rate) | `helm/ironpass/dashboards/ironpass.json`, loaded by `helm/ironpass/templates/grafana-dashboard.yaml` |

The ServiceMonitor and the dashboard are part of the app chart, so they are deployed together with the application.

## Install

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --version 92.9.0 \
  -f monitoring/kube-prometheus-stack-values.yaml \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set-json 'prometheus.prometheusSpec.serviceMonitorNamespaceSelector={}' \
  --wait --timeout 10m
```

The two `--set` lines matter. By default Prometheus only looks at ServiceMonitors that carry the release label of the chart, and only in its own namespace. With `serviceMonitorSelectorNilUsesHelmValues=false` and an empty `serviceMonitorNamespaceSelector` it finds the ServiceMonitor from any namespace, so the one in `ironpass` is picked up. The same settings are in the values file. `scripts/install-monitoring.sh` runs this command.

## Open Prometheus and Grafana

Grafana's admin password is created by the chart and stored in a Kubernetes secret. Read it like this (the password is never written into this repo):

```bash
kubectl get secret kube-prometheus-stack-grafana -n monitoring -o jsonpath='{.data.admin-password}' | base64 -d; echo
```

The user name is `admin`. Port-forward from WSL so Windows can reach it:

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80 --address 0.0.0.0
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090 --address 0.0.0.0
```

- Grafana: http://localhost:3001 then Dashboards, IronPass Overview
- Prometheus targets: http://localhost:9090/targets (the `ironpass-backend` target must be UP)

## Check that the app is scraped

```bash
kubectl get servicemonitor -n ironpass
kubectl get cm -n ironpass -l grafana_dashboard=1
```

Send some traffic with `scripts/load-test.sh` and the panels fill with data.

# Live demo guide

All commands run in the WSL terminal, inside the repo folder, unless it says Windows.
The address of the load balancer only works **while the cluster is running**. After
`scripts/teardown.sh` it is gone.

## Open the folder from Windows

```bash
explorer.exe .
```

## Addresses (valid only while the cluster is running)

| What | Address |
| --- | --- |
| App through the Traefik Ingress | http://ab0016c869bfc4402884a19059ee9f8e-691966334.ap-south-1.elb.amazonaws.com |
| Backend API docs and metrics | `kubectl port-forward` below, then http://localhost:8001/docs and http://localhost:8001/metrics |
| Grafana | http://localhost:3001 |
| Prometheus | http://localhost:9090 |
| GitHub repo | https://github.com/brixdorf/ironpass-devops-capstone |
| Local compose app | http://localhost:3000 |

If the hostname is lost, read it again:

```bash
kubectl get svc traefik -n traefik -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'; echo
```

## Grafana login

User: `admin`. The chart creates a random password and keeps it in a Kubernetes secret, so it is
not written down anywhere. Print it when you need it:

```bash
kubectl get secret kube-prometheus-stack-grafana -n monitoring -o jsonpath='{.data.admin-password}' | base64 -d; echo
```

Do not show this command's output on screen while recording. Grafana is only reachable through the
port-forward, never from the internet.

## Port-forwards for Windows

Run each in its own terminal. The address 0.0.0.0 lets the Windows browser reach them on localhost.

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80 --address 0.0.0.0
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090 --address 0.0.0.0
kubectl port-forward -n ironpass svc/ironpass-backend 8001:8000 --address 0.0.0.0
```

Then open from Windows:

- http://localhost:3001 for Grafana (dashboard "IronPass Overview")
- http://localhost:9090/targets for Prometheus targets
- http://localhost:8001/docs for the Swagger page and http://localhost:8001/metrics for raw metrics

If kubectl says the credentials expired, run `aws login` again and retry. Port 8001 is used
for the backend so it does not clash with `docker compose` on port 8000.

## 10 step demo order

This follows Part O of the course README.

1. **Application.** Open the load balancer address. Sign up a member, then check in an expired member (Rohan Das) and show the rejection message.
2. **API.** Open http://localhost:8001/docs. Run GET `/api/members`, POST `/api/checkins` for an expired member (409), POST `/api/plans` with `"plan_type": "WEEKLY"` (422), and DELETE a member.
3. **Database.** Show the table inside the cluster:
   ```bash
   kubectl exec -n ironpass deploy/ironpass-postgres -- sh -c 'psql -U $POSTGRES_USER -d $POSTGRES_DB -c "select id, full_name, status, expires_on from members order by id;"'
   ```
4. **Git.** Make a small change (for example the tagline in `frontend/src/App.jsx`), then `git add -A && git commit -m "Change dashboard tagline" && git push`.
5. **CI, security and registry.** Run `gh run watch` or open the Actions tab. Show the pytest job, the Trivy steps, the smoke test on kind, then the GHCR package with the SHA tag. The deploy job updates the cluster.
6. **Terraform.** Show `terraform/` in the editor, then `terraform -chdir=terraform output` and `aws eks describe-cluster --name ironpass-eks --query cluster.status`.
7. **Kubernetes and Helm.**
   ```bash
   kubectl get pods -n ironpass
   kubectl get svc -n ironpass
   helm list -n ironpass
   helm history ironpass -n ironpass
   ```
8. **Ingress and HPA.** Reload the load balancer address in the browser, then run the load script and watch the autoscaler in a second terminal:
   ```bash
   ./scripts/load-test.sh
   kubectl get hpa -n ironpass -w
   ```
9. **Monitoring.** Show the Prometheus targets page (ironpass-backend UP) and the Grafana dashboard while the load test runs.
10. **Failure simulation.**
    ```bash
    kubectl apply -f troubleshooting/broken-service.yaml
    kubectl get pods -n ironpass --show-labels -l lab=broken-service
    kubectl get svc,endpoints -n ironpass ironpass-broken-service
    # fix the selector in the file (tier: web), then
    kubectl apply -f troubleshooting/broken-service.yaml
    kubectl delete -f troubleshooting/
    ```

## After the demo

Run `./scripts/teardown.sh --dry-run` to show the plan, and `./scripts/teardown.sh --yes` when you are
finished. The AWS cluster costs money while it is running. After the teardown, add the teardown date
to the README and commit `docs/terraform-destroy-output.txt`.

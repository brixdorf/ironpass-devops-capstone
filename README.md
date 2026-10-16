<p align="center">
  <a href="https://docs.google.com/presentation/d/REPLACE_WITH_SLIDES_ID/edit?usp=sharing"><img alt="Presentation on Google Slides" src="https://img.shields.io/badge/PRESENTATION-Google%20Slides-F4B400?style=for-the-badge&logo=googleslides&logoColor=white"></a>
  <a href="IronPass-Presentation.pdf"><img alt="PDF copy of the presentation" src="https://img.shields.io/badge/PDF%20copy-in%20this%20repo-6B7280?style=flat-square&logo=adobeacrobatreader&logoColor=white"></a>
  &nbsp;&nbsp;
  <a href="https://www.loom.com/share/REPLACE_WITH_VIDEO_ID"><img alt="Video walkthrough on Loom" src="https://img.shields.io/badge/VIDEO-Loom%20walkthrough-625DF5?style=for-the-badge&logo=loom&logoColor=white"></a>
</p>

# IronPass

[![CI](https://github.com/brixdorf/ironpass-devops-capstone/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/brixdorf/ironpass-devops-capstone/actions/workflows/ci-cd.yml)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?logo=helm&logoColor=white)
![Traefik](https://img.shields.io/badge/Traefik-24A1C1?logo=traefikproxy&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-844FBA?logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EKS-FF9900?logo=amazonaws&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)

## What is IronPass?

IronPass is a small web app for a gym front desk. Staff sign new members up, see who is active or expired, and check people in at the door. One rule keeps the gym safe: **if a member's plan has expired, the check-in is refused.**

The project shows the whole journey of an app, from code on a laptop to a monitored Kubernetes cluster on AWS. It was built by a student to learn DevOps.

```mermaid
flowchart LR
  dev[Developer] -->|git push| gh[GitHub]
  gh --> ci[GitHub Actions]
  ci -->|test, build, scan| img[Images in GHCR]
  tf[Terraform] --> aws[AWS VPC and EKS]
  img -->|helm upgrade| aws
  aws --> app[IronPass pods]
  app -->|/metrics| prom[Prometheus]
  prom --> graf[Grafana]
```

> **Live on AWS while recording, then torn down to avoid cost.** The cluster is not running when you read this. See the video and the screenshots below.

## Quick start

You need Docker. Two commands:

```bash
git clone https://github.com/brixdorf/ironpass-devops-capstone.git && cd ironpass-devops-capstone
docker compose up --build
```

Open http://localhost:3000 for the app and http://localhost:8000/docs for the API pages. Stop it with `docker compose down`.

<p align="center">
  <img src="docs/screenshots/01-app-running-localhost-3000.png" alt="IronPass dashboard in the browser after a new member was added" width="760">
</p>

The sections below hold the technical details. Each one is collapsed, click a title to open it.

<details>
<summary><b>Tech stack</b></summary>

| Layer | What | Version |
| --- | --- | --- |
| Frontend | React and Vite, served by nginx (unprivileged) | React 19.3, Vite 8.3, nginx 1.30 |
| Backend | Python, FastAPI, SQLAlchemy, Alembic, pydantic-settings, prometheus-client | Python 3.14, FastAPI 0.143 |
| Database | PostgreSQL | 18.6 |
| Tests | pytest on an in-memory SQLite database | pytest 9.1 |
| Containers | Docker and Docker Compose | |
| CI/CD | GitHub Actions, Trivy, GitHub Container Registry | |
| Infrastructure | Terraform: VPC and EKS on AWS (`ap-south-1`) | Terraform 1.16, AWS provider 6.69 |
| Kubernetes | Helm chart, Traefik Ingress, HPA, metrics-server | Helm 4.3, Traefik 3.7 |
| Monitoring | Prometheus and Grafana (kube-prometheus-stack) | chart 92.9 |

Every version is pinned. The full list with the date it was checked is in [docs/VERSIONS.md](docs/VERSIONS.md).

Why Traefik: the Kubernetes project retired ingress-nginx in March 2026 (no more fixes or security patches). Traefik is maintained, implements the normal Ingress API, and is used the same way on kind, Minikube and EKS.

</details>

<details>
<summary><b>API endpoints with example requests</b></summary>

The API is plain REST under `/api`. Allowed enum values are written in capital letters: plan types `DAY_PASS`, `MONTHLY`, `QUARTERLY`, `ANNUAL`, and member statuses `ACTIVE`, `FROZEN`, `CANCELLED` (`EXPIRED` is worked out from the expiry date).

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/health` | Liveness: the process is running. It never touches the database. |
| GET | `/ready` | Readiness: the API can reach the database. Returns 503 if it cannot. |
| GET | `/metrics` | Prometheus text format. |
| GET | `/api/plans` | List plans. |
| POST | `/api/plans` | Create a plan. |
| GET | `/api/members` | List members. Filters: `plan_id`, `status` (for example `EXPIRED`). |
| GET | `/api/members/{id}` | One member. 404 if missing. |
| POST | `/api/members` | Sign up a member. |
| PUT | `/api/members/{id}` | Change name, plan or status. |
| POST | `/api/members/{id}/renew` | Extend the plan from today or from the old end date. |
| DELETE | `/api/members/{id}` | Delete a member. |
| POST | `/api/checkins` | Check a member in. **Rejected with 409 when the plan is expired.** |
| GET | `/api/checkins` | Latest check-ins. |
| GET | `/api/stats` | Numbers for the dashboard cards. |
| GET | `/api/activity` | Latest check-ins and signups together (the activity feed). |

Real requests and real answers from the running stack (`docker compose up`):

```console
$ curl -s http://localhost:8000/health
{"status":"ok"}

$ curl -s -X POST http://localhost:8000/api/members -H 'Content-Type: application/json' -d '{"full_name":"Asha Verma","email":"asha@example.com","plan_id":2}'
{"id":9,"full_name":"Asha Verma","email":"asha@example.com","plan_id":2,"plan_name":"Monthly","plan_type":"MONTHLY","status":"ACTIVE","effective_status":"ACTIVE","joined_on":"2026-10-16","expires_on":"2026-11-15"}

$ curl -s -X POST http://localhost:8000/api/checkins -H 'Content-Type: application/json' -d '{"member_id":9}'
{"id":5,"member_id":9,"member_name":"Asha Verma","checked_in_at":"2026-10-16T06:20:39.834481Z"}

$ curl -s -X POST http://localhost:8000/api/checkins -H 'Content-Type: application/json' -d '{"member_id":5}'
{"detail":"Check-in rejected, membership is EXPIRED"}

$ curl -s -X POST http://localhost:8000/api/plans -H 'Content-Type: application/json' -d '{"name":"Weekly","plan_type":"WEEKLY","price_cents":1500,"duration_days":7}'
{"detail":[{"type":"enum","loc":["body","plan_type"],"msg":"Input should be 'DAY_PASS', 'MONTHLY', 'QUARTERLY' or 'ANNUAL'","input":"WEEKLY","ctx":{"expected":"'DAY_PASS', 'MONTHLY', 'QUARTERLY' or 'ANNUAL'"}}]}

$ curl -s http://localhost:8000/api/members/999
{"detail":"Member not found"}

$ curl -s http://localhost:8000/api/stats
{"total_members":9,"active_members":6,"expired_members":2,"frozen_members":1,"check_ins_today":3,"expiring_soon":1}
```

<img src="docs/screenshots/05-api-swagger-docs.png" alt="Swagger page at localhost:8000/docs" width="700">
<img src="docs/screenshots/05b-api-swagger-try-it-out.png" alt="Swagger Try it out with the 409 answer for an expired member" width="700">
<img src="docs/screenshots/05c-api-health.png" alt="localhost:8000/health" width="500">
<img src="docs/screenshots/05d-api-metrics.png" alt="localhost:8000/metrics" width="700">
<img src="docs/screenshots/25-checkin-rejected-expired-plan.png" alt="The UI refuses the check-in of an expired member" width="700">
<img src="docs/screenshots/24-database-members-table.png" alt="The members table inside PostgreSQL on the cluster" width="600">

</details>

<details>
<summary><b>Run the backend and frontend by hand (no Docker)</b></summary>

You need Python 3.14, Node 24 and a PostgreSQL database.

**Backend**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

export DATABASE_URL=postgresql+psycopg://ironpass:ironpass@localhost:5432/ironpass

alembic upgrade head                      # always first: it creates the tables and the demo data
uvicorn app.main:app --port 8000          # then start the API
```

**Always run `alembic upgrade head` before `uvicorn`.** The app never creates tables by itself. All tables come from the Alembic migrations in `backend/alembic/versions/`. The Docker image does this for you: its start command is `alembic upgrade head && uvicorn ...`.

**Frontend**

```bash
cd frontend
npm ci
npm run dev        # http://localhost:5173, /api is forwarded to http://localhost:8000
```

**Tests** (they build their own tables on SQLite, no database needed):

```bash
cd backend
pytest -v
```

<img src="docs/screenshots/02-pytest-verbose.png" alt="pytest -v output, 32 passed" width="700">

The 32 tests cover validation (a wrong plan type returns 422), 404 for missing members, the expired plan rule, the stats endpoint and the activity feed.

</details>

<details>
<summary><b>Run with Docker</b></summary>

Both images run as a normal user, not root.

| Image | Base | User | Port |
| --- | --- | --- | --- |
| `backend/Dockerfile` | `python:3.14.8-slim-trixie` | uid 10001 | 8000 |
| `frontend/Dockerfile` (multi-stage: Node builds, nginx serves) | `nginxinc/nginx-unprivileged:1.30.6-alpine3.24` | nginx (uid 101) | 8080 |

Each folder has its own `.dockerignore` (`node_modules`, `.git`, `__pycache__`, `.venv`, `.env`).

```bash
docker build -t ironpass-backend backend
docker build -t ironpass-frontend frontend
docker run --rm -e BACKEND_URL=http://my-backend:8000 -p 3000:8080 ironpass-frontend
```

The nginx address of the backend is **not** written into the image. The container reads the variable `BACKEND_URL` when it starts, so the same image works in Compose (`http://backend:8000`) and in Kubernetes (`http://ironpass-backend:8000`).

</details>

<details>
<summary><b>Run with Docker Compose</b></summary>

```bash
docker compose up --build
```

Three services start in the right order: PostgreSQL first, then the backend, then the frontend. The services find each other **by service name** (`postgres`, `backend`), not by IP address.

- `depends_on` alone only waits until a container has **started**, not until it is **ready**, and the backend would exit if PostgreSQL were not accepting connections yet. So PostgreSQL has a health check (`pg_isready` for this project's user and database), the backend waits for it with `condition: service_healthy`, has its own health check (`/ready`), and `restart: on-failure`. The frontend waits for a healthy backend.
- The database lives in a named volume, so records survive `docker compose down`. **`docker compose down -v` deletes the data.**

Proof: three clean starts in a row, everything healthy each time, and a record that survives a restart.

<img src="docs/screenshots/04-docker-compose-up-and-ps.png" alt="docker compose up and docker compose ps" width="800">
<img src="docs/screenshots/04b-docker-compose-three-clean-starts.png" alt="Three clean starts, all healthy" width="800">
<img src="docs/screenshots/04c-docker-compose-data-persists.png" alt="A record is still there after docker compose down and up" width="700">

</details>

<details>
<summary><b>Run on Kubernetes (kind or Minikube, and EKS)</b></summary>

Two ways to deploy, for two jobs:

| Folder | Used for |
| --- | --- |
| `k8s/` | plain manifests (namespace, deployments, services, a real Postgres pod). The pipeline applies them on a throwaway kind cluster as a smoke test. |
| `helm/ironpass/` | the real deployment: backend and frontend with 2 replicas each, ClusterIP services, Ingress, HPA, PostgreSQL with a PVC, ServiceMonitor and the Grafana dashboard. `values-dev.yaml` is for kind or Minikube, `values-prod.yaml` is for EKS. |

**On kind** (Minikube works the same way):

```bash
kind create cluster --name ironpass
docker build -t ironpass-backend:dev backend && docker build -t ironpass-frontend:dev frontend
kind load docker-image ironpass-backend:dev ironpass-frontend:dev --name ironpass

helm repo add traefik https://traefik.github.io/charts
helm upgrade --install traefik traefik/traefik --version 42.0.0 -n traefik --create-namespace \
  -f k8s/traefik-values.yaml --set service.spec.type=ClusterIP --wait
kubectl apply -f k8s/namespace.yaml
helm upgrade --install ironpass helm/ironpass -n ironpass -f helm/ironpass/values-dev.yaml --wait

kubectl port-forward -n traefik svc/traefik 8080:80     # then open http://localhost:8080
```

**On EKS** (after Terraform, see the next block):

```bash
aws eks update-kubeconfig --region ap-south-1 --name ironpass-eks
./scripts/bootstrap-cluster.sh        # namespace, storage class, Traefik, metrics-server
./scripts/install-monitoring.sh       # Prometheus and Grafana
helm upgrade --install ironpass helm/ironpass -n ironpass -f helm/ironpass/values-prod.yaml \
  --set backend.tag=<commit-sha> --set frontend.tag=<commit-sha> --wait
```

The Ingress sends `/` to the frontend Service (port 80) and `/api` to the backend Service (port 8000). `scripts/check-helm-wiring.py` checks in the pipeline that those Services exist with those ports. Probes: `/health` for liveness and `/ready` for readiness. Every container has resource requests, which the HPA needs.

Install, upgrade and rollback with `helm history` and `helm rollback`:

<img src="docs/screenshots/13-kubectl-get-nodes.png" alt="kubectl get nodes" width="800">
<img src="docs/screenshots/14-kubectl-get-pods.png" alt="kubectl get pods" width="700">
<img src="docs/screenshots/15-kubectl-get-svc-ingress.png" alt="kubectl get svc and ingress" width="800">
<img src="docs/screenshots/16-helm-list.png" alt="helm list" width="700">
<img src="docs/screenshots/16b-helm-history-and-rollback.png" alt="helm history and helm rollback" width="800">
<img src="docs/screenshots/17-app-through-traefik-ingress.png" alt="The app through the Ingress load balancer" width="700">
<img src="docs/screenshots/17b-ingress-curl.png" alt="curl through the load balancer, / and /api both answer" width="700">
<img src="docs/screenshots/26-ingress-nginx-removed.png" alt="ingress-nginx uninstalled and its old load balancer gone" width="800">

**Autoscaling.** The HPA scales the backend between 2 and 6 pods at 50 percent CPU. `scripts/load-test.sh` sends traffic to a real path (`/api/members`, `/api/stats`, `/api/checkins`) until the autoscaler adds pods. metrics-server provides the CPU numbers.

<img src="docs/screenshots/19-hpa-before-load.png" alt="kubectl get hpa before the load" width="700">
<img src="docs/screenshots/19b-hpa-during-load.png" alt="kubectl get hpa during the load, 6 replicas" width="700">
<img src="docs/screenshots/19c-load-test-script-timeline.png" alt="Timeline printed by the load script" width="800">

</details>

<details>
<summary><b>Terraform (VPC and EKS on AWS)</b></summary>

Files in `terraform/`: `versions.tf`, `main.tf`, `variables.tf`, `outputs.tf` and `terraform.tfvars.example`. Real `terraform.tfvars` and state files stay out of git.

- A VPC with 2 public and 2 private subnets and one NAT gateway. The availability zones are looked up with `aws_availability_zones`, so changing the region works.
- An EKS cluster (Kubernetes 1.35) with a managed node group of 2 nodes.
- A GitHub OIDC provider, an IAM role limited to the `main` branch of this repository, and an EKS access entry limited to the `ironpass` namespace. The pipeline signs in with short-lived tokens, **no AWS keys are stored in GitHub**.
- Every resource is tagged `Project=ironpass` and `ManagedBy=terraform`.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars     # optional
terraform init
terraform fmt -check && terraform validate
terraform plan
terraform apply
```

Note on the nodes: this AWS account is on the free plan and refuses `t3.medium`, so the nodes are `c7i-flex.large` (same 2 vCPU and 4 GiB).

<img src="docs/screenshots/09-terraform-plan.png" alt="terraform plan, 62 to add" width="800">
<img src="docs/screenshots/10-aws-vpc-subnets.png" alt="aws describe VPC and subnets" width="800">
<img src="docs/screenshots/11-aws-eks-cluster-and-nodegroup.png" alt="aws describe EKS cluster and node group" width="800">
<img src="docs/screenshots/12-terraform-outputs.png" alt="terraform output" width="700">
<img src="docs/screenshots/22-github-oidc-role.png" alt="GitHub OIDC role and EKS access entry" width="800">
<img src="docs/screenshots/09b-terraform-module-upgrade.png" alt="plan and apply of the module upgrade, then no changes" width="700">
<img src="docs/screenshots/27-teardown-dry-run.png" alt="The teardown script ready, dry run" width="800">

</details>

<details>
<summary><b>CI/CD pipeline (GitHub Actions)</b></summary>

`.github/workflows/ci-cd.yml` runs on every push to `main` and on pull requests (branches are written as a list).

| Job | What happens |
| --- | --- |
| Test and build frontend | `pytest -v`, `npm run build`, `helm lint` and the Ingress wiring check. A failure stops everything. |
| Build, scan and push (backend and frontend) | Each image is built **once**. Trivy scans **that** image and fails the job on any fixable HIGH or CRITICAL finding. Only then the **same** image is pushed to GHCR, tagged with the commit SHA. |
| Smoke test on kind | A temporary kind cluster runs the scanned images with the plain manifests in `k8s/` and a real Postgres pod, then `curl` calls `/health`, `/ready` and `/api`. |
| Deploy to EKS | Helm upgrade with the SHA tag, signed in with the GitHub OIDC role. Runs only on `main` and only when the repository variable `DEPLOY_ENABLED` is `true`. |

Details worth knowing:

- Registry: GitHub Container Registry only, with the built-in `GITHUB_TOKEN`. No Docker Hub. No user name is written in the workflow, it uses `github.repository_owner`.
- Tags are commit SHAs, not `latest`. The packages are public.
- Every action is pinned to a full commit SHA with the version in a comment. For Trivy the action version is v0.35.0, the release that the March 2026 security advisory (CVE-2026-33634) lists as safe.
- The Trivy gate was proven once: on a throwaway branch an old `urllib3` was added on purpose, the scan failed (7 HIGH findings), the push and the deploy were skipped, then the branch was deleted.
- After the cluster is torn down, `scripts/teardown.sh` sets `DEPLOY_ENABLED` to `false` and removes the stale AWS variables, so the next push does not fail against a cluster that no longer exists.

<img src="docs/screenshots/06-github-actions-green-run.png" alt="Green GitHub Actions run with the job list" width="800">
<img src="docs/screenshots/06b-github-repository-page.png" alt="The GitHub repository page" width="800">
<img src="docs/screenshots/03-github-commit-history.png" alt="Commit history" width="800">
<img src="docs/screenshots/07-ghcr-packages.png" alt="GitHub Container Registry packages" width="800">
<img src="docs/screenshots/08-trivy-scan-backend-clean.png" alt="Trivy step output, backend image clean" width="800">
<img src="docs/screenshots/08b-trivy-scan-frontend-clean.png" alt="Trivy step output, frontend image clean" width="800">
<img src="docs/screenshots/08c-trivy-gate-red-run.png" alt="Red run: the Trivy gate stops the pipeline" width="800">
<img src="docs/screenshots/08d-trivy-gate-findings.png" alt="The findings that made the red run fail" width="800">
<img src="docs/screenshots/08e-ci-kind-smoke-test.png" alt="Smoke test on kind inside the pipeline" width="800">

See [docs/SECURITY.md](docs/SECURITY.md) for what Trivy scanned and what the result means.

</details>

<details>
<summary><b>Monitoring (Prometheus and Grafana)</b></summary>

The backend exposes `/metrics`. Prometheus scrapes it through a ServiceMonitor, Grafana shows a dashboard that is provisioned as code (request rate, latency, error rate, replicas). Both the ServiceMonitor and the dashboard are part of the app's Helm chart, so they are deployed together with the application.

```bash
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace --version 92.9.0 \
  -f monitoring/kube-prometheus-stack-values.yaml \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set-json 'prometheus.prometheusSpec.serviceMonitorNamespaceSelector={}'
```

The two `--set` lines let Prometheus find the ServiceMonitor in any namespace. The Grafana password is read from the cluster secret, it is never stored in this repo:

```bash
kubectl get secret kube-prometheus-stack-grafana -n monitoring -o jsonpath='{.data.admin-password}' | base64 -d; echo
```

More in [monitoring/README.md](monitoring/README.md).

<img src="docs/screenshots/18-metrics-curl.png" alt="curl of the backend metrics" width="800">
<img src="docs/screenshots/20-prometheus-targets.png" alt="Prometheus targets, ironpass-backend UP" width="800">
<img src="docs/screenshots/21-grafana-dashboard.png" alt="Grafana dashboard with live data" width="800">

</details>

<details>
<summary><b>Troubleshooting lab</b></summary>

Three manifests in `troubleshooting/` are broken on purpose, with the exact diagnosis steps in [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md). Each one was applied on the cluster with `kubectl apply -f`, diagnosed with `get pods -n`, `describe pod`, `get events`, `get endpoints` and `get pods --show-labels`, fixed and removed.

| Lab | Symptom | Cause and fix |
| --- | --- | --- |
| `broken-image.yaml` | `ImagePullBackOff` | the image tag does not exist, use a tag that does |
| `broken-service.yaml` | pod Running, Service has no endpoints | selector `tier: webb` does not match label `tier: web` |
| `broken-crashloop.yaml` | `CrashLoopBackOff` | the container exits because `DB_HOST` is not set, add the variable |

<img src="docs/screenshots/23-troubleshooting-lab1-image.png" alt="Lab 1, ImagePullBackOff" width="800">
<img src="docs/screenshots/23b-troubleshooting-lab2-service.png" alt="Lab 2, Service without endpoints" width="800">
<img src="docs/screenshots/23c-troubleshooting-lab3-crashloop.png" alt="Lab 3, CrashLoopBackOff" width="800">

</details>

<details>
<summary><b>Rubric: where to find the proof for M1 to M10</b></summary>

| Module | Topic | Folder or screenshot |
| --- | --- | --- |
| M1 | Application | `backend/`, `frontend/`, `docker-compose.yml`, `docs/screenshots/01-app-running-localhost-3000.png` |
| M2 | Testing | `backend/tests/`, `backend/pytest.ini`, `docs/screenshots/02-pytest-verbose.png` |
| M3 | Git and GitHub | `.gitignore`, `docs/screenshots/03-github-commit-history.png` |
| M4 | Docker | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `docs/screenshots/04-docker-compose-up-and-ps.png` |
| M5 | CI/CD | `.github/workflows/ci-cd.yml`, `docs/screenshots/06-github-actions-green-run.png`, `docs/screenshots/07-ghcr-packages.png` |
| M6 | Trivy | `docs/SECURITY.md`, `docs/screenshots/08-trivy-scan-backend-clean.png`, `docs/screenshots/08c-trivy-gate-red-run.png` |
| M7 | Terraform | `terraform/`, `docs/screenshots/09-terraform-plan.png`, `docs/screenshots/10-aws-vpc-subnets.png`, `docs/screenshots/11-aws-eks-cluster-and-nodegroup.png`, `scripts/teardown.sh` |
| M8 | Kubernetes and Helm | `k8s/`, `helm/ironpass/`, `docs/screenshots/14-kubectl-get-pods.png`, `docs/screenshots/16-helm-list.png`, `docs/screenshots/17-app-through-traefik-ingress.png` |
| M9 | Observability | `monitoring/`, `docs/screenshots/18-metrics-curl.png`, `docs/screenshots/20-prometheus-targets.png`, `docs/screenshots/21-grafana-dashboard.png` |
| M10 | Docs and demo | this README, `docs/DEMO.md`, `IronPass-Presentation.pptx`, `docs/VIDEO_SCRIPT.md` |

No criterion was skipped, so no feature had to replace another one.

The `terraform destroy` proof for M7 comes from `scripts/teardown.sh`, which saves its output in `docs/terraform-destroy-output.txt`.

</details>

<details>
<summary><b>Repository structure and cleanup</b></summary>

```text
backend/            FastAPI app (app/ with main, models, schemas, db, config, routers, services), Alembic, tests
frontend/           React and Vite app, nginx config template
k8s/                plain manifests for the kind smoke test, namespace, storage class, Traefik values
helm/ironpass/      Helm chart (dev and prod values, dashboard, ServiceMonitor, HPA)
terraform/          VPC, EKS and GitHub OIDC
monitoring/         kube-prometheus-stack values and notes
troubleshooting/    three broken manifests for practice
scripts/            bootstrap, monitoring install, load test, smoke test, teardown
docs/               demo guide, security note, versions, troubleshooting guide, video script, screenshots
.github/workflows/  the CI/CD pipeline
IronPass-Presentation.pptx, IronPass-Presentation.pdf
docker-compose.yml
```

**Cleanup.** The AWS cluster costs money while it runs. `scripts/teardown.sh --dry-run` prints the steps. `scripts/teardown.sh --yes` turns the deploy switch off, removes the Helm releases, volumes and load balancer, runs `terraform destroy`, checks that nothing tagged `Project=ironpass` is left, and removes the stale GitHub variables.

</details>

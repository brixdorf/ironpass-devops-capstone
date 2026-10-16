<a id="top"></a>
<h1 align="center">IronPass</h1>

<p align="center">A gym membership app, taken from code on a laptop to a monitored Kubernetes cluster on AWS.</p>

<!-- EDIT THIS LINE (1 of 2): replace REPLACE_WITH_SLIDES_ID with the id of your Google Slides link -->
<p align="center"><img src="docs/assets/icons/presentation.svg" width="28" height="28" alt="Presentation" align="absmiddle"> <b>Presentation, Google Slides:</b> Read the 20 slide walkthrough<br><a href="https://docs.google.com/presentation/d/REPLACE_WITH_SLIDES_ID/edit?usp=sharing">https://docs.google.com/presentation/d/REPLACE_WITH_SLIDES_ID/edit?usp=sharing</a></p>

<!-- EDIT THIS LINE (2 of 2): replace REPLACE_WITH_VIDEO_ID with the id of your Loom link -->
<p align="center"><img src="docs/assets/icons/video.svg" width="28" height="28" alt="Video" align="absmiddle"> <b>Video, Loom:</b> Watch the 2 minute demo<br><a href="https://www.loom.com/share/REPLACE_WITH_VIDEO_ID">https://www.loom.com/share/REPLACE_WITH_VIDEO_ID</a></p>

<p align="center"><img src="docs/assets/icons/pdf.svg" width="28" height="28" alt="PDF copy" align="absmiddle"> <b>PDF copy:</b> The same slides as a PDF, in this repo<br><a href="IronPass-Presentation.pdf">IronPass-Presentation.pdf</a></p>

<p align="center">
  <img src="docs/screenshots/01-app-running-localhost-3000.png" alt="The IronPass dashboard with the member table, the check-in panel and the activity feed" width="800">
  <br><i>The IronPass dashboard running locally, after a new member was signed up.</i>
</p>

<table align="center"><tr><td align="center" width="150"><img src="docs/assets/icons/glance-endpoints.svg" width="28" height="28" alt="Endpoints"><br><b>15</b><br><sub>endpoints</sub></td><td align="center" width="150"><img src="docs/assets/icons/glance-tests.svg" width="28" height="28" alt="Tests"><br><b>32</b><br><sub>tests</sub></td><td align="center" width="150"><img src="docs/assets/icons/glance-pipeline.svg" width="28" height="28" alt="Pipeline time"><br><b>5m 8s</b><br><sub>pipeline</sub></td><td align="center" width="150"><img src="docs/assets/icons/glance-pods.svg" width="28" height="28" alt="Pods"><br><b>5</b><br><sub>pods</sub></td><td align="center" width="150"><img src="docs/assets/icons/glance-targets.svg" width="28" height="28" alt="Prometheus targets"><br><b>19</b><br><sub>targets</sub></td></tr></table>

IronPass is a small web app for a gym front desk. Staff sign new members up, see who is active or expired, and check people in at the door. The project shows the whole journey of an app, from the first commit to a monitored cluster. A student built it to learn DevOps.

> [!IMPORTANT]
> **The one rule that matters:** if a member's plan has expired, the check-in is refused. The API answers with status 409 and the screen shows a red message with the expiry date. This rule is enforced in the API and covered by tests.

<h2><img src="docs/assets/icons/built-with.svg" width="28" height="28" alt="Built with" align="absmiddle"> Built with</h2>

<table>
<tr><td><b>Code</b></td><td><img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"> <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"> <img alt="React" src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB"> <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white"></td></tr>
<tr><td><b>Ship</b></td><td><img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white"> <img alt="GitHub Actions" src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white"> <img alt="Trivy" src="https://img.shields.io/badge/Trivy-1904DA?style=flat-square&logo=trivy&logoColor=white"></td></tr>
<tr><td><b>Run</b></td><td><img alt="Kubernetes" src="https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white"> <img alt="Helm" src="https://img.shields.io/badge/Helm-0F1689?style=flat-square&logo=helm&logoColor=white"> <img alt="Traefik" src="https://img.shields.io/badge/Traefik-24A1C1?style=flat-square&logo=traefikproxy&logoColor=white"> <img alt="Terraform" src="https://img.shields.io/badge/Terraform-844FBA?style=flat-square&logo=terraform&logoColor=white"> <img alt="AWS EKS" src="https://img.shields.io/badge/AWS%20EKS-FF9900?style=flat-square&logo=amazonaws&logoColor=white"></td></tr>
<tr><td><b>Watch</b></td><td><img alt="Prometheus" src="https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white"> <img alt="Grafana" src="https://img.shields.io/badge/Grafana-F46800?style=flat-square&logo=grafana&logoColor=white"></td></tr>
</table>

<h2><img src="docs/assets/icons/how-it-works.svg" width="28" height="28" alt="How it works" align="absmiddle"> How it works in five steps</h2>

1. **You write code** and run `git push`.
2. **GitHub Actions** tests the code, builds two images (backend and frontend), scans them for known security holes and stores them in a registry called GHCR.
3. **Terraform** has already built the network and the Kubernetes cluster on AWS (EKS).
4. **Helm** installs the new images on the cluster. **Traefik** sends visitors to the right pod, and the autoscaler adds pods when traffic grows.
5. **Prometheus** collects numbers from the app and **Grafana** draws them as graphs.

```mermaid
flowchart LR
  dev["Developer<br/>git push"] --> gh["GitHub"]
  gh --> ci["Actions<br/>test, scan"]
  ci --> img["Images<br/>in GHCR"]
  img --> aws["AWS EKS<br/>Helm deploy"]
  tf["Terraform"] --> aws
  aws --> app["IronPass<br/>pods"]
  app --> prom["Prometheus"]
  prom --> graf["Grafana"]

  classDef code fill:#0B1020,stroke:#C6FF3D,stroke-width:2px,color:#C6FF3D
  classDef ship fill:#0B1020,stroke:#FFB547,stroke-width:2px,color:#FFB547
  classDef infra fill:#0B1020,stroke:#A58BFF,stroke-width:2px,color:#A58BFF
  classDef watch fill:#0B1020,stroke:#22D3EE,stroke-width:2px,color:#22D3EE
  class dev,gh code
  class ci,img ship
  class tf,aws,app infra
  class prom,graf watch
```

> [!NOTE]
> **Live on AWS while recording, then torn down to avoid cost.** The cluster is not running when you read this. See the video and the screenshots below.

<p align="right"><a href="#top">Back to top</a></p>

<h2><img src="docs/assets/icons/quick-start.svg" width="28" height="28" alt="Quick start" align="absmiddle"> Quick start</h2>

> [!TIP]
> You only need Docker. Two commands start the database, the API and the web page.

```bash
git clone https://github.com/brixdorf/ironpass-devops-capstone.git && cd ironpass-devops-capstone
docker compose up --build
```

Open http://localhost:3000 for the app and http://localhost:8000/docs for the API pages. Stop it with `docker compose down`.

<p align="center">
  <img src="docs/screenshots/01b-app-mobile-390.png" alt="The same page on a phone, 390 pixels wide: summary cards first, then the member cards" width="260">
  <br><i>The same page on a phone. The table turns into cards.</i>
</p>

The sections below hold the technical details. Each one is collapsed, click a title to open it.

<details>
<summary><img src="docs/assets/icons/built-with.svg" width="24" height="24" alt="Tech stack" align="absmiddle"> <b>Tech stack</b></summary>

This table lists every tool in the project and the exact version that was tested.

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

<p align="right"><a href="#top">Back to top</a></p>

</details>

<details>
<summary><img src="docs/assets/icons/api.svg" width="24" height="24" alt="endpoints" align="absmiddle"> <b>API endpoints with example requests</b></summary>

An API is how the web page talks to the server, and REST means each address does one clear job, for example listing members. This part shows every address with real requests and real answers.

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

<p align="right"><a href="#top">Back to top</a></p>

</details>

<details>
<summary><img src="docs/assets/icons/run-by-hand.svg" width="24" height="24" alt="Run by hand" align="absmiddle"> <b>Run the backend and frontend by hand (no Docker)</b></summary>

Use this if you want to start the backend (the server code with the rules and the database access) and the frontend (the web page) yourself, without Docker.

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

<p align="right"><a href="#top">Back to top</a></p>

</details>

<details>
<summary><img src="docs/assets/icons/docker.svg" width="24" height="24" alt="Docker" align="absmiddle"> <b>Run with Docker</b></summary>

Docker packs an app and everything it needs into an image (a ready-to-run package), so it behaves the same on every computer.

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

<p align="right"><a href="#top">Back to top</a></p>

</details>

<details>
<summary><img src="docs/assets/icons/compose.svg" width="24" height="24" alt="Docker Compose" align="absmiddle"> <b>Run with Docker Compose</b></summary>

Docker Compose starts several containers, here the database, the backend and the frontend, together with one command.

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

<p align="right"><a href="#top">Back to top</a></p>

</details>

<details>
<summary><img src="docs/assets/icons/kubernetes.svg" width="24" height="24" alt="Kubernetes" align="absmiddle"> <b>Run on Kubernetes (kind or Minikube, and EKS)</b></summary>

Kubernetes (K8s) runs containers on a group of machines and restarts them when they fail. Helm is its package manager: one command installs the whole app. kind and Minikube are small clusters for a laptop, EKS is the Kubernetes service on AWS.

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

<p align="right"><a href="#top">Back to top</a></p>

</details>

<details>
<summary><img src="docs/assets/icons/terraform.svg" width="24" height="24" alt="Terraform" align="absmiddle"> <b>Terraform (VPC and EKS on AWS)</b></summary>

Terraform builds cloud networks and servers from text files (Infrastructure as Code), so the whole setup can be created or removed with one command.

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

<p align="right"><a href="#top">Back to top</a></p>

</details>

<details>
<summary><img src="docs/assets/icons/cicd.svg" width="24" height="24" alt="CI/CD" align="absmiddle"> <b>CI/CD pipeline (GitHub Actions)</b></summary>

CI/CD means every code change is tested, built, scanned and delivered automatically. GitHub Actions is the tool that runs these steps, and Trivy is the scanner that looks for known security holes.

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

<p align="right"><a href="#top">Back to top</a></p>

</details>

<details>
<summary><img src="docs/assets/icons/monitoring.svg" width="24" height="24" alt="Monitoring" align="absmiddle"> <b>Monitoring (Prometheus and Grafana)</b></summary>

Prometheus collects numbers (metrics) from the app and Grafana draws them as graphs, so you can see if the app is healthy.

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

<p align="right"><a href="#top">Back to top</a></p>

</details>

<details>
<summary><img src="docs/assets/icons/troubleshooting.svg" width="24" height="24" alt="Troubleshooting" align="absmiddle"> <b>Troubleshooting lab</b></summary>

Three Kubernetes manifests that are broken on purpose, to practise finding and fixing common problems.

Three manifests in `troubleshooting/` are broken on purpose, with the exact diagnosis steps in [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md). Each one was applied on the cluster with `kubectl apply -f`, diagnosed with `get pods -n`, `describe pod`, `get events`, `get endpoints` and `get pods --show-labels`, fixed and removed.

| Lab | Symptom | Cause and fix |
| --- | --- | --- |
| `broken-image.yaml` | `ImagePullBackOff` | the image tag does not exist, use a tag that does |
| `broken-service.yaml` | pod Running, Service has no endpoints | selector `tier: webb` does not match label `tier: web` |
| `broken-crashloop.yaml` | `CrashLoopBackOff` | the container exits because `DB_HOST` is not set, add the variable |

<img src="docs/screenshots/23-troubleshooting-lab1-image.png" alt="Lab 1, ImagePullBackOff" width="800">
<img src="docs/screenshots/23b-troubleshooting-lab2-service.png" alt="Lab 2, Service without endpoints" width="800">
<img src="docs/screenshots/23c-troubleshooting-lab3-crashloop.png" alt="Lab 3, CrashLoopBackOff" width="800">

<p align="right"><a href="#top">Back to top</a></p>

</details>

<details>
<summary><img src="docs/assets/icons/rubric.svg" width="24" height="24" alt="Rubric" align="absmiddle"> <b>Rubric: where to find the proof for M1 to M10</b></summary>

One row per course module: the points it is worth, what the project does for it, where to look, and whether it is done.

| Module | Points | What it covers | Proof | Done |
| --- | --- | --- | --- | --- |
| M1 Application | 10 | React frontend, FastAPI backend, PostgreSQL, 15 endpoints, one real business rule | [backend](backend), [frontend](frontend), [screenshot](docs/screenshots/01-app-running-localhost-3000.png) | <img src="docs/assets/icons/check.svg" width="20" height="20" alt="Done" align="absmiddle"> |
| M2 Testing | 10 | 32 pytest tests: validation, 404, the expired plan rule, stats | [tests](backend/tests), [screenshot](docs/screenshots/02-pytest-verbose.png) | <img src="docs/assets/icons/check.svg" width="20" height="20" alt="Done" align="absmiddle"> |
| M3 Git and GitHub | 5 | 100+ small commits, `.gitignore`, no secrets in the repository | [.gitignore](.gitignore), [screenshot](docs/screenshots/03-github-commit-history.png) | <img src="docs/assets/icons/check.svg" width="20" height="20" alt="Done" align="absmiddle"> |
| M4 Docker | 10 | Two non-root images, multi-stage frontend, Compose with health checks | [backend/Dockerfile](backend/Dockerfile), [frontend/Dockerfile](frontend/Dockerfile), [docker-compose.yml](docker-compose.yml), [screenshot](docs/screenshots/04-docker-compose-up-and-ps.png) | <img src="docs/assets/icons/check.svg" width="20" height="20" alt="Done" align="absmiddle"> |
| M5 CI/CD | 15 | Test, build once, scan, push the same image to GHCR, kind smoke test, deploy to EKS | [ci-cd.yml](.github/workflows/ci-cd.yml), [run](docs/screenshots/06-github-actions-green-run.png), [registry](docs/screenshots/07-ghcr-packages.png) | <img src="docs/assets/icons/check.svg" width="20" height="20" alt="Done" align="absmiddle"> |
| M6 Trivy | 5 | Both images scanned, the pipeline fails on fixable HIGH or CRITICAL findings | [SECURITY.md](docs/SECURITY.md), [clean scan](docs/screenshots/08-trivy-scan-backend-clean.png), [red run](docs/screenshots/08c-trivy-gate-red-run.png) | <img src="docs/assets/icons/check.svg" width="20" height="20" alt="Done" align="absmiddle"> |
| M7 Terraform | 15 | VPC, EKS, node group, GitHub OIDC role, teardown script | [terraform](terraform), [plan](docs/screenshots/09-terraform-plan.png), [VPC](docs/screenshots/10-aws-vpc-subnets.png), [EKS](docs/screenshots/11-aws-eks-cluster-and-nodegroup.png), [teardown.sh](scripts/teardown.sh) | <img src="docs/assets/icons/check.svg" width="20" height="20" alt="Done" align="absmiddle"> |
| M8 Kubernetes and Helm | 15 | Helm chart, Ingress, HPA, probes, PVC, troubleshooting lab | [k8s](k8s), [helm/ironpass](helm/ironpass), [pods](docs/screenshots/14-kubectl-get-pods.png), [helm list](docs/screenshots/16-helm-list.png), [ingress](docs/screenshots/17-app-through-traefik-ingress.png) | <img src="docs/assets/icons/check.svg" width="20" height="20" alt="Done" align="absmiddle"> |
| M9 Observability | 10 | /metrics, ServiceMonitor, Prometheus targets, Grafana dashboard as code | [monitoring](monitoring), [targets](docs/screenshots/20-prometheus-targets.png), [dashboard](docs/screenshots/21-grafana-dashboard.png) | <img src="docs/assets/icons/check.svg" width="20" height="20" alt="Done" align="absmiddle"> |
| M10 Presentation and docs | 5 | This README, demo guide, 20 slides, video script | [DEMO.md](docs/DEMO.md), [slides (PPTX)](IronPass-Presentation.pptx), [slides (PDF)](IronPass-Presentation.pdf), [VIDEO_SCRIPT.md](docs/VIDEO_SCRIPT.md) | <img src="docs/assets/icons/check.svg" width="20" height="20" alt="Done" align="absmiddle"> |

No criterion was skipped, so no feature had to replace another one.

The `terraform destroy` proof for M7 comes from `scripts/teardown.sh`, which saves its output in `docs/terraform-destroy-output.txt`.

<p align="right"><a href="#top">Back to top</a></p>

</details>

<details>
<summary><img src="docs/assets/icons/structure.svg" width="24" height="24" alt="Repository structure" align="absmiddle"> <b>Repository structure and cleanup</b></summary>

Where things live in this repository, and how to remove the AWS resources when you are done.

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

<p align="right"><a href="#top">Back to top</a></p>

</details>

---

<p align="center"><sub>Built by <a href="https://github.com/brixdorf">brixdorf</a> as a DevOps capstone project. Where everything lives: see <i>Repository structure and cleanup</i> above.<br>
Fonts in the website and the slides: Unbounded, DM Sans, JetBrains Mono and Inter, all under the SIL Open Font License. Icons: Lucide (ISC) and Simple Icons (CC0).<br>
<a href="#top">Back to top</a></sub></p>

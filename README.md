<p align="center">
  <a href="https://docs.google.com/presentation/d/REPLACE_WITH_SLIDES_ID/edit?usp=sharing"><img alt="Presentation on Google Slides" src="https://img.shields.io/badge/PRESENTATION-Google%20Slides-F4B400?style=for-the-badge&logo=googleslides&logoColor=white"></a>
  <a href="docs/IronPass-Presentation.pdf"><img alt="PDF copy" src="https://img.shields.io/badge/PDF%20copy-in%20this%20repo-6B7280?style=flat-square&logo=adobeacrobatreader&logoColor=white"></a>
  &nbsp;&nbsp;
  <a href="https://www.loom.com/share/REPLACE_WITH_VIDEO_ID"><img alt="Video walkthrough on Loom" src="https://img.shields.io/badge/VIDEO-Loom%20walkthrough-625DF5?style=for-the-badge&logo=loom&logoColor=white"></a>
</p>

# IronPass

IronPass is a small gym membership app. Staff sign members up, check them in at the front desk, and the API refuses a check-in when the member's plan has expired. This repo takes it all the way from code to a monitored Kubernetes cluster on AWS.

[![CI](https://github.com/brixdorf/ironpass-devops-capstone/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/brixdorf/ironpass-devops-capstone/actions/workflows/ci-cd.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?logo=helm&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-844FBA?logo=terraform&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-EKS-FF9900?logo=amazonaws&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)

## How it flows

```mermaid
flowchart LR
  dev[Developer] -->|git push| gh[GitHub]
  gh --> ci[GitHub Actions]
  ci -->|pytest, build, Trivy| img[Images in GHCR]
  tf[Terraform] --> aws[AWS VPC and EKS]
  img -->|helm upgrade| aws
  aws --> app[IronPass pods]
  app -->|/metrics| prom[Prometheus]
  prom --> graf[Grafana]
```

## Run it in 2 minutes

You need Docker. Then:

```bash
git clone https://github.com/brixdorf/ironpass-devops-capstone.git
cd ironpass-devops-capstone
docker compose up --build
```

Open http://localhost:3000. The API docs are at http://localhost:8000/docs.
Stop it with `docker compose down` (add `-v` to wipe the database).

## The pipeline

Every push to `main` runs `.github/workflows/ci-cd.yml`.

| Stage | What happens |
| --- | --- |
| Test | `pytest` runs against SQLite. A failure stops everything. |
| Build | The React app is built, then both Docker images are built. |
| Scan | Trivy checks both images and fails on fixable HIGH or CRITICAL issues. |
| Push | Images go to GHCR, tagged with the commit SHA. |
| Deploy | Helm installs the new tag on EKS, signed in with GitHub OIDC (no AWS keys). |

## Where to find the proof

| Module | Topic | Folder or screenshot |
| --- | --- | --- |
| M1 | Application | `backend/`, `frontend/`, `docs/screenshots/01-app-running-localhost-3000.png` |
| M2 | Tests | `backend/tests/`, `docs/screenshots/02-pytest-passing.png` |
| M3 | Git and GitHub | commit history, `docs/screenshots/03-git-history.png` |
| M4 | Docker | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `docs/screenshots/04-docker-compose-up.png` |
| M5 | CI/CD | `.github/workflows/`, `docs/screenshots/06-github-actions-green.png`, `docs/screenshots/07-ghcr-backend.png`, `docs/screenshots/07-ghcr-frontend.png` |
| M6 | Trivy | `docs/SECURITY.md`, `docs/screenshots/08-trivy-scan.png` |
| M7 | Terraform | `terraform/`, `docs/screenshots/09-terraform-plan.png`, `docs/screenshots/10-aws-vpc-subnets.png`, `docs/screenshots/11-aws-eks-cluster.png`, `docs/screenshots/12-terraform-apply-outputs.png` |
| M8 | Kubernetes and Helm | `helm/ironpass/`, `k8s/`, `docs/screenshots/14-kubectl-pods.png`, `docs/screenshots/16-helm-list.png`, `docs/screenshots/17-ingress-app.png`, `docs/screenshots/19-hpa-scaling.png` |
| M9 | Monitoring | `monitoring/`, `docs/screenshots/18-metrics-endpoint.png`, `docs/screenshots/20-prometheus-targets.png`, `docs/screenshots/21-grafana-dashboard.png` |
| M10 | Docs and demo | this README, `docs/DEMO.md`, `docs/IronPass-Presentation.pptx`, `docs/VIDEO_SCRIPT.md` |

The broken manifests for the troubleshooting lab are in `troubleshooting/`.

## Clean up

The cluster costs money while it is up. `scripts/teardown.sh --dry-run` shows the steps and `scripts/teardown.sh --yes` removes the Helm releases and load balancer first, then runs `terraform destroy`, then checks that nothing tagged `Project=ironpass` is left.

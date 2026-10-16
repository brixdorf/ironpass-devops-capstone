# Versions

Every version below was looked up on 2026-10-16 from the official source
(npm, PyPI, the Terraform registry, GitHub releases, Docker Hub, endoflife.date)
and pinned exactly. Nothing uses `latest`.

## Runtimes and base images

| Tool | Version used | Checked | Note |
| --- | --- | --- | --- |
| Python | 3.14.8 (`python:3.14.8-slim-trixie`) | 2026-10-16 | 3.15.0 came out two weeks ago, but some packages (pyyaml) have no wheels for it yet |
| Node.js | 24.22.0 LTS (`node:24.22.0-alpine3.24`) | 2026-10-16 | 24 is the active LTS line, 26 becomes LTS on 2026-10-28 |
| nginx | 1.30.6 stable (`nginxinc/nginx-unprivileged:1.30.6-alpine3.24`) | 2026-10-16 | mainline is 1.31.7 |
| PostgreSQL | 18.6 (`postgres:18.6-alpine3.24`) | 2026-10-16 | newest major |

## Backend packages (`backend/requirements*.txt`)

| Package | Version | Checked |
| --- | --- | --- |
| fastapi | 0.143.2 | 2026-10-16 |
| uvicorn[standard] | 0.54.0 | 2026-10-16 |
| sqlalchemy | 2.1.4 | 2026-10-16 |
| alembic | 1.20.0 | 2026-10-16 |
| psycopg[binary] | 3.3.6 | 2026-10-16 |
| pydantic | 2.14.1 | 2026-10-16 |
| pydantic-settings | 2.16.0 | 2026-10-16 |
| prometheus-client | 0.26.0 | 2026-10-16 |
| pytest | 9.1.1 | 2026-10-16 |
| httpx2 | 2.13.1 | 2026-10-16 |

Notes:

- `httpx` 0.28.1 is still the newest `httpx`, but Starlette's test client now warns that it is deprecated and asks for `httpx2`, so the tests use `httpx2`.
- The metrics are written with `prometheus-client` directly (own middleware and a check-in counter). `prometheus-fastapi-instrumentator` 8.1.0 is not used.

## Frontend packages (`frontend/package.json`, locked in `package-lock.json`)

| Package | Version | Checked |
| --- | --- | --- |
| react | 19.3.1 | 2026-10-16 |
| react-dom | 19.3.1 | 2026-10-16 |
| vite | 8.3.4 | 2026-10-16 |
| @vitejs/plugin-react | 6.1.2 | 2026-10-16 |

## Infrastructure

| Tool | Version used | Checked | Note |
| --- | --- | --- | --- |
| Terraform CLI | 1.16.6 | 2026-10-16 | `required_version = "~> 1.16"` |
| AWS provider | 6.69.1 (`~> 6.69`) | 2026-10-16 | the VPC module needs >= 6.28 and the EKS module needs >= 6.59, so one constraint satisfies both |
| VPC module | 6.7.3 (`~> 6.7`) | 2026-10-16 | |
| EKS module | 21.29.0 (`~> 21.29`) | 2026-10-16 | |
| Kubernetes on EKS | 1.35 | 2026-10-16 | still in standard support until 2027-03-27, so it stays |

Note on Kubernetes: EKS now offers 1.36 and 1.37 (released 2026-10-01). The live
cluster was **not** upgraded to them, because a control plane upgrade takes a
long time and could disturb the demo. This is a note only.

Note on the nodes: the worker nodes are 2 x `c7i-flex.large` and not `t3.medium`.
This AWS account is on the free plan and it refuses `t3.medium`
("not eligible for Free Tier"). `c7i-flex.large` has the same size (2 vCPU, 4 GiB).
The comment is also in `terraform/main.tf`.

Note on the module upgrade: the live cluster was built with EKS module 20.x and VPC module 5.x.
Moving to 21.x and 6.x was planned first and applied only after the plan showed no
replacement of the cluster, the VPC or the nodes (2 added, 5 changed, 4 destroyed,
all small IAM and add-on items). Two node settings are pinned in `main.tf` so the module's
new defaults do not replace the nodes.

## Kubernetes tooling

| Tool | Version used | Checked | Note |
| --- | --- | --- | --- |
| Helm CLI | 4.3.1 | 2026-10-16 | |
| Chart `apiVersion` | v2 | 2026-10-16 | the current chart format |
| Traefik chart | 42.0.0 (Traefik 3.7.14) | 2026-10-16 | Traefik 3.7 is a supported release line |
| metrics-server chart | 3.14.0 (metrics-server 0.9.0) | 2026-10-16 | |
| kube-prometheus-stack chart | 92.9.0 (Prometheus Operator 0.94.1) | 2026-10-16 | |
| kind | 0.33.0 | 2026-10-16 | used in the pipeline smoke test |

Ingress controller: ingress-nginx is retired (no releases, fixes or security
patches after March 2026), so IronPass uses **Traefik** on every environment
(kind, Minikube and EKS). Traefik implements the standard Kubernetes Ingress API,
is actively maintained, and installs with its official Helm chart
(`k8s/traefik-values.yaml`, `ingressClassName: traefik`).

## GitHub Actions

All actions are pinned to the full commit SHA, with the version in a comment on the same line.

| Action | Version | Commit | Checked |
| --- | --- | --- | --- |
| actions/checkout | v7.0.1 | 3d3c42e5aac5 | 2026-10-16 |
| actions/setup-python | v7.0.0 | 5fda3b95a4ea | 2026-10-16 |
| actions/setup-node | v7.1.0 | 949feb2413d6 | 2026-10-16 |
| docker/setup-buildx-action | v4.4.1 | f87e5991a6d7 | 2026-10-16 |
| docker/build-push-action | v7.4.0 | c3c9e263c25d | 2026-10-16 |
| docker/login-action | v4.6.0 | dbcb813823bd | 2026-10-16 |
| aquasecurity/trivy-action | v0.35.0 | 57a97c7e7821 | 2026-10-16 |
| helm/kind-action | v1.15.1 | 1544676c07bb | 2026-10-16 |
| actions/upload-artifact | v7.0.2 | cf430e030ddb | 2026-10-16 |
| actions/download-artifact | v8.0.2 | 9000827ccba6 | 2026-10-16 |
| aws-actions/configure-aws-credentials | v6.3.0 | e1253824e5c1 | 2026-10-16 |
| azure/setup-helm | v5.0.1 | 9bc31f4ebc9c | 2026-10-16 |
| Runner image | `ubuntu-26.04` | | 2026-10-16 |

Trivy: the action is `v0.35.0` because the March 2026 supply chain advisory for the Trivy
GitHub Actions (CVE-2026-33634) lists that release as the one that was not affected, and it
is an immutable release. The newer `v0.36.0` is not named in the advisory, so it is not used.
The Trivy program itself is set to `v0.76.0` (the newest release) with the `version` input.

## Tools used to make the docs

| Tool | Version | Checked |
| --- | --- | --- |
| Playwright | 1.64.1 | 2026-10-16 |
| python-pptx | 1.0.2 | 2026-10-16 |
| Fonts (Google Fonts) | Unbounded, DM Sans, JetBrains Mono | 2026-10-16 |

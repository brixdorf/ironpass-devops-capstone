import re, sys, json
old = open(sys.argv[1]).read()
facts = json.load(open(sys.argv[2]))

IC = "docs/assets/icons"
def tile(name, alt, size=24):
    return f'<img src="{IC}/{name}.svg" width="{size}" height="{size}" alt="{alt}" align="absmiddle">'

BACK = '\n<p align="right"><a href="#top">Back to top</a></p>\n'

# ---------- take the old collapsed blocks ----------
blocks = re.findall(r"<details>\n<summary><b>(.*?)</b></summary>\n\n(.*?)\n\n</details>", old, re.S)
body = {t: b for t, b in blocks}

meta = {
 "Tech stack": ("built-with", "Tech stack", "This table lists every tool in the project and the exact version that was tested."),
 "API endpoints with example requests": ("api", "API endpoints", "An API is how the web page talks to the server, and REST means each address does one clear job, for example listing members. This part shows every address with real requests and real answers."),
 "Run the backend and frontend by hand (no Docker)": ("run-by-hand", "Run by hand", "Use this if you want to start the backend (the server code with the rules and the database access) and the frontend (the web page) yourself, without Docker."),
 "Run with Docker": ("docker", "Docker", "Docker packs an app and everything it needs into an image (a ready-to-run package), so it behaves the same on every computer."),
 "Run with Docker Compose": ("compose", "Docker Compose", "Docker Compose starts several containers, here the database, the backend and the frontend, together with one command."),
 "Run on Kubernetes (kind or Minikube, and EKS)": ("kubernetes", "Kubernetes", "Kubernetes (K8s) runs containers on a group of machines and restarts them when they fail. Helm is its package manager: one command installs the whole app. kind and Minikube are small clusters for a laptop, EKS is the Kubernetes service on AWS."),
 "Terraform (VPC and EKS on AWS)": ("terraform", "Terraform", "Terraform builds cloud networks and servers from text files (Infrastructure as Code), so the whole setup can be created or removed with one command."),
 "CI/CD pipeline (GitHub Actions)": ("cicd", "CI/CD", "CI/CD means every code change is tested, built, scanned and delivered automatically. GitHub Actions is the tool that runs these steps, and Trivy is the scanner that looks for known security holes."),
 "Monitoring (Prometheus and Grafana)": ("monitoring", "Monitoring", "Prometheus collects numbers (metrics) from the app and Grafana draws them as graphs, so you can see if the app is healthy."),
 "Troubleshooting lab": ("troubleshooting", "Troubleshooting", "Three Kubernetes manifests that are broken on purpose, to practise finding and fixing common problems."),
 "Repository structure and cleanup": ("structure", "Repository structure", "Where things live in this repository, and how to remove the AWS resources when you are done."),
}

def section(title):
    icon, alt, intro = meta[title]
    short = {
     "API endpoints with example requests": "API endpoints with example requests",
     "Run the backend and frontend by hand (no Docker)": "Run the backend and frontend by hand (no Docker)",
    }.get(title, title)
    return (f'<details>\n<summary>{tile(icon, alt)} <b>{short}</b></summary>\n\n'
            f'{intro}\n\n{body[title]}\n{BACK}\n</details>\n')

rubric = f'''<details>
<summary>{tile("rubric", "Rubric")} <b>Rubric: where to find the proof for M1 to M10</b></summary>

One row per course module: the points it is worth, what the project does for it, where to look, and whether it is done.

| Module | Points | What it covers | Proof | Done |
| --- | --- | --- | --- | --- |
| M1 Application | 10 | React frontend, FastAPI backend, PostgreSQL, {facts["endpoints"]} endpoints, one real business rule | [backend](backend), [frontend](frontend), [screenshot](docs/screenshots/01-app-running-localhost-3000.png) | {tile("check", "Done", 20)} |
| M2 Testing | 10 | {facts["tests"]} pytest tests: validation, 404, the expired plan rule, stats | [tests](backend/tests), [screenshot](docs/screenshots/02-pytest-verbose.png) | {tile("check", "Done", 20)} |
| M3 Git and GitHub | 5 | {facts["commits"]} small commits, `.gitignore`, no secrets in the repository | [.gitignore](.gitignore), [screenshot](docs/screenshots/03-github-commit-history.png) | {tile("check", "Done", 20)} |
| M4 Docker | 10 | Two non-root images, multi-stage frontend, Compose with health checks | [backend/Dockerfile](backend/Dockerfile), [frontend/Dockerfile](frontend/Dockerfile), [docker-compose.yml](docker-compose.yml), [screenshot](docs/screenshots/04-docker-compose-up-and-ps.png) | {tile("check", "Done", 20)} |
| M5 CI/CD | 15 | Test, build once, scan, push the same image to GHCR, kind smoke test, deploy to EKS | [ci-cd.yml](.github/workflows/ci-cd.yml), [run](docs/screenshots/06-github-actions-green-run.png), [registry](docs/screenshots/07-ghcr-packages.png) | {tile("check", "Done", 20)} |
| M6 Trivy | 5 | Both images scanned, the pipeline fails on fixable HIGH or CRITICAL findings | [SECURITY.md](docs/SECURITY.md), [clean scan](docs/screenshots/08-trivy-scan-backend-clean.png), [red run](docs/screenshots/08c-trivy-gate-red-run.png) | {tile("check", "Done", 20)} |
| M7 Terraform | 15 | VPC, EKS, node group, GitHub OIDC role, teardown script | [terraform](terraform), [plan](docs/screenshots/09-terraform-plan.png), [VPC](docs/screenshots/10-aws-vpc-subnets.png), [EKS](docs/screenshots/11-aws-eks-cluster-and-nodegroup.png), [teardown.sh](scripts/teardown.sh) | {tile("check", "Done", 20)} |
| M8 Kubernetes and Helm | 15 | Helm chart, Ingress, HPA, probes, PVC, troubleshooting lab | [k8s](k8s), [helm/ironpass](helm/ironpass), [pods](docs/screenshots/14-kubectl-get-pods.png), [helm list](docs/screenshots/16-helm-list.png), [ingress](docs/screenshots/17-app-through-traefik-ingress.png) | {tile("check", "Done", 20)} |
| M9 Observability | 10 | /metrics, ServiceMonitor, Prometheus targets, Grafana dashboard as code | [monitoring](monitoring), [targets](docs/screenshots/20-prometheus-targets.png), [dashboard](docs/screenshots/21-grafana-dashboard.png) | {tile("check", "Done", 20)} |
| M10 Presentation and docs | 5 | This README, demo guide, 20 slides, video script | [DEMO.md](docs/DEMO.md), [slides (PPTX)](IronPass-Presentation.pptx), [slides (PDF)](IronPass-Presentation.pdf), [VIDEO_SCRIPT.md](docs/VIDEO_SCRIPT.md) | {tile("check", "Done", 20)} |

No criterion was skipped, so no feature had to replace another one.

The `terraform destroy` proof for M7 comes from `scripts/teardown.sh`, which saves its output in `docs/terraform-destroy-output.txt`.
{BACK}
</details>
'''

def badge(label, logo, color, text="white"):
    return f'<img alt="{label}" src="https://img.shields.io/badge/{label.replace(" ", "%20")}-{color}?style=flat-square&logo={logo}&logoColor={text}">'

built = f'''<table>
<tr><td><b>Code</b></td><td>{badge("Python", "python", "3776AB")} {badge("FastAPI", "fastapi", "009688")} {badge("React", "react", "20232A", "61DAFB")} {badge("PostgreSQL", "postgresql", "4169E1")}</td></tr>
<tr><td><b>Ship</b></td><td>{badge("Docker", "docker", "2496ED")} {badge("GitHub Actions", "githubactions", "2088FF")} {badge("Trivy", "trivy", "1904DA")}</td></tr>
<tr><td><b>Run</b></td><td>{badge("Kubernetes", "kubernetes", "326CE5")} {badge("Helm", "helm", "0F1689")} {badge("Traefik", "traefikproxy", "24A1C1")} {badge("Terraform", "terraform", "844FBA")} {badge("AWS EKS", "amazonaws", "FF9900")}</td></tr>
<tr><td><b>Watch</b></td><td>{badge("Prometheus", "prometheus", "E6522C")} {badge("Grafana", "grafana", "F46800")}</td></tr>
</table>'''

def fact(icon, alt, number, label):
    return f'<td align="center" width="150"><img src="{IC}/{icon}.svg" width="28" height="28" alt="{alt}"><br><b>{number}</b><br><sub>{label}</sub></td>'

glance = '<table align="center"><tr>' + "".join([
    fact("glance-endpoints", "Endpoints", facts["endpoints"], "API endpoints"),
    fact("glance-tests", "Tests", facts["tests"], "tests pass"),
    fact("glance-pipeline", "Pipeline time", facts["pipeline"], "pipeline run"),
    fact("glance-pods", "Pods", facts["pods"], "pods on EKS"),
    fact("glance-targets", "Prometheus targets", facts["targets"], "Prometheus targets up"),
]) + "</tr></table>"

top = f'''<a id="top"></a>
<h1 align="center">IronPass</h1>

<p align="center">A gym membership app, taken from code on a laptop to a monitored Kubernetes cluster on AWS.</p>

<!-- EDIT THIS LINE (1 of 2): replace REPLACE_WITH_SLIDES_ID with the id of your Google Slides link -->
<p align="center"><img src="{IC}/presentation.svg" width="28" height="28" alt="Presentation" align="absmiddle"> <b>Presentation, Google Slides:</b> Read the 20 slide walkthrough<br><a href="https://docs.google.com/presentation/d/REPLACE_WITH_SLIDES_ID/edit?usp=sharing">https://docs.google.com/presentation/d/REPLACE_WITH_SLIDES_ID/edit?usp=sharing</a></p>

<!-- EDIT THIS LINE (2 of 2): replace REPLACE_WITH_VIDEO_ID with the id of your Loom link -->
<p align="center"><img src="{IC}/video.svg" width="28" height="28" alt="Video" align="absmiddle"> <b>Video, Loom:</b> Watch the 2 minute demo<br><a href="https://www.loom.com/share/REPLACE_WITH_VIDEO_ID">https://www.loom.com/share/REPLACE_WITH_VIDEO_ID</a></p>

<p align="center"><img src="{IC}/pdf.svg" width="28" height="28" alt="PDF copy" align="absmiddle"> <b>PDF copy:</b> The same slides as a PDF, in this repo<br><a href="IronPass-Presentation.pdf">IronPass-Presentation.pdf</a></p>

<p align="center">
  <img src="docs/screenshots/01-app-running-localhost-3000.png" alt="The IronPass dashboard with the member table, the check-in panel and the activity feed" width="800">
  <br><i>The IronPass dashboard running locally, after a new member was signed up.</i>
</p>

{glance}

IronPass is a small web app for a gym front desk. Staff sign new members up, see who is active or expired, and check people in at the door. The project shows the whole journey of an app, from the first commit to a monitored cluster. A student built it to learn DevOps.

> [!IMPORTANT]
> **The one rule that matters:** if a member's plan has expired, the check-in is refused. The API answers with status 409 and the screen shows a red message with the expiry date. This rule is enforced in the API and covered by tests.

<h2><img src="{IC}/built-with.svg" width="28" height="28" alt="Built with" align="absmiddle"> Built with</h2>

{built}

<h2><img src="{IC}/how-it-works.svg" width="28" height="28" alt="How it works" align="absmiddle"> How it works in five steps</h2>

1. **You write code** and run `git push`.
2. **GitHub Actions** tests the code, builds two images (backend and frontend), scans them for known security holes and stores them in a registry called GHCR.
3. **Terraform** has already built the network and the Kubernetes cluster on AWS (EKS).
4. **Helm** installs the new images on the cluster. **Traefik** sends visitors to the right pod, and the autoscaler adds pods when traffic grows.
5. **Prometheus** collects numbers from the app and **Grafana** draws them as graphs.

```mermaid
flowchart LR
  dev["Developer"] -->|git push| gh["GitHub"]
  gh --> ci["GitHub Actions"]
  ci -->|test, build, scan| img["Images in GHCR"]
  tf["Terraform"] --> aws["AWS VPC and EKS"]
  img -->|helm upgrade| aws
  aws --> app["IronPass pods"]
  app -->|/metrics| prom["Prometheus"]
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
{BACK}
<h2><img src="{IC}/quick-start.svg" width="28" height="28" alt="Quick start" align="absmiddle"> Quick start</h2>

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

'''

order = ["Tech stack", "API endpoints with example requests", "Run the backend and frontend by hand (no Docker)", "Run with Docker", "Run with Docker Compose", "Run on Kubernetes (kind or Minikube, and EKS)", "Terraform (VPC and EKS on AWS)", "CI/CD pipeline (GitHub Actions)", "Monitoring (Prometheus and Grafana)", "Troubleshooting lab"]
parts = [section(t) for t in order] + [rubric, section("Repository structure and cleanup")]

footer = f'''
---

<p align="center"><sub>Built by <a href="https://github.com/brixdorf">brixdorf</a> as a DevOps capstone project. Where everything lives: see <i>Repository structure and cleanup</i> above.<br>
Fonts in the website and the slides: Unbounded, DM Sans, JetBrains Mono and Inter, all under the SIL Open Font License. Icons: Lucide (ISC) and Simple Icons (CC0).<br>
<a href="#top">Back to top</a></sub></p>
'''
open(sys.argv[3], "w").write(top + "\n".join(parts) + footer)

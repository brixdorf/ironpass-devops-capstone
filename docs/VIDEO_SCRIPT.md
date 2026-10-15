# Video script (about 3 minutes)

Read each scene aloud while you record the screen. The line in brackets is what should be on screen.

1. [README top of the repo with the badges and the flow diagram]
Hi, I am Romit. This is IronPass, a gym membership app. I built it to show how an app travels from my laptop to a monitored Kubernetes cluster on AWS.

2. [Browser on the IronPass dashboard, then the check-in form]
This is the app. It has a React frontend, a FastAPI backend and a PostgreSQL database. I can sign up a member, filter the table by plan, and check someone in. One real rule lives in the API. If a member's plan has expired, the check-in is rejected. Here you can see the error message.

3. [Terminal running pytest, all tests green]
There are seventeen tests, and they all pass. One of them checks the expired plan rule. They run on a throwaway SQLite database, so the real data is never touched.

4. [GitHub Actions run page, all jobs green]
Every push to main starts this pipeline. It runs the tests, builds the frontend, builds both Docker images, scans them, and pushes them to the registry. If a test fails, nothing gets built.

5. [Trivy step in the run log]
Here is the Trivy scan. It fails the build on any fixable high or critical problem. My first runs failed, so I upgraded the libraries and the base image. Now both images are clean.

6. [GHCR package page showing the commit SHA tag]
The images are tagged with the commit SHA, so I can trace any running pod back to the exact code.

7. [VS Code or terminal on the terraform folder, then aws eks describe-cluster output]
The infrastructure is written in Terraform. It creates a VPC with public and private subnets, one NAT gateway, and an EKS cluster with two t3 medium nodes. It also sets up GitHub OIDC, so the pipeline signs in to AWS without any stored keys.

8. [Terminal with kubectl get pods, kubectl get svc, helm list]
Helm deploys the app. Backend and frontend each run two replicas, behind ClusterIP services. Each pod has health and readiness probes, and resource requests, so Kubernetes knows when to restart it and when to send it traffic. The database runs in the cluster too, with a persistent volume, so the data survives a restart.

9. [Browser on the load balancer address]
The Ingress sends slash to the frontend and slash api to the backend. This is the live app on the load balancer address.

10. [Terminal running the load script next to kubectl get hpa]
Now I send traffic with a small load script. As the backend CPU goes up, the horizontal pod autoscaler adds more backend pods. You can watch the replica count climb from two to more.

11. [Grafana IronPass dashboard]
Prometheus scrapes the metrics endpoint of the backend, and the target shows as up. Grafana shows it on a dashboard. You can see the request rate, the latency and the error rate move during the load test, and the number of replicas change.

12. [Terminal with the broken service manifest and kubectl get endpoints]
I also made two broken manifests for practice. This service has a typo in its selector, so it has no endpoints. Fixing the label fixes it. The big lesson for me is that every tool has one job, and the pipeline joins them together.

13. [Slide with the thank you message]
Thank you for watching.

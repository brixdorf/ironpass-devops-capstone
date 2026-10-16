# Video script (about 2 minutes)

Read each scene aloud while you record the screen. The line in brackets is what should be on screen.

1. [Browser on the IronPass dashboard, then the check-in form]
Hi, I am Romit. This is IronPass, a gym membership app. It has a React frontend, a FastAPI backend and a PostgreSQL database. Staff sign members up and check them in at the door. If a member's plan has expired, the check-in is refused. Here you can see the message.

2. [Terminal in the repo, a small edit in the frontend, then git commit and git push]
Now I change one line of the app, commit it with a clear message, and push it to GitHub.

3. [GitHub Actions run page with the jobs going green]
That push starts the pipeline. It runs the tests, builds the frontend, builds both Docker images, and scans them with Trivy. If a test fails, nothing is built. The scan fails the build if it finds a serious problem that has a fix. Then the images are pushed to the registry with the commit hash as the tag.

4. [Smoke test job, then the deploy job in the same run]
The same images are tried on a small temporary cluster first. If that works, the pipeline deploys to Amazon EKS with Helm. It signs in with a short lived token, so no AWS keys are stored in GitHub.

5. [Terminal with kubectl get pods, kubectl get svc, helm list]
Terraform built the network and the cluster. Helm runs two copies of the backend and two of the frontend, and the Traefik ingress sends traffic to them.

6. [Browser on the load balancer address showing the updated app]
This is the new version, live on the load balancer address.

7. [Terminal running the load script next to kubectl get hpa]
I send some traffic. As the load grows, the autoscaler adds more backend pods. You can watch the number go up from two to six.

8. [Prometheus targets page, then the Grafana dashboard]
Prometheus scrapes the metrics of the backend, and Grafana shows the request rate, the latency and the errors while the load runs. The dashboard is set up as code, so Grafana loads it by itself.

9. [Terminal with a broken manifest and kubectl describe pod]
I also practised fixing broken deployments, like a missing image or a crash loop.

10. [Slide with the thank you message]
Thank you for watching.

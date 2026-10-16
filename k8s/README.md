# k8s/ and helm/ (what each one is for)

| Folder | Used for |
| --- | --- |
| `k8s/` | Plain manifests. The pipeline applies them on a throwaway kind cluster for a smoke test. Also the namespace and storage class that the EKS cluster needs. |
| `helm/ironpass/` | The real deployment. Helm installs it on EKS (`values-prod.yaml`) or on kind and Minikube (`values-dev.yaml`). |

Files in `k8s/`:

- `namespace.yaml` creates the `ironpass` namespace.
- `postgres.yaml`, `backend.yaml`, `frontend.yaml` are the smoke test stack. The database uses an emptyDir.
- `storageclass-gp3.yaml` is the EBS storage class for the EKS database volume.
- `traefik-values.yaml` is the Helm values file for the Ingress controller.

Apply with `kubectl apply -f FILE`.

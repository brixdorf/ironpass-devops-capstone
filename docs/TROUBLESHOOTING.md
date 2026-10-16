# Troubleshooting

When something in Kubernetes does not work, ask the cluster in this order.
Always pass the namespace with `-n`. The app lives in the namespace `ironpass`.

```bash
kubectl get pods -n ironpass                       # 1. what state is each pod in?
kubectl describe pod POD_NAME -n ironpass          # 2. why? read the Events at the bottom
kubectl get events -n ironpass --sort-by=.lastTimestamp   # 3. what happened recently?
kubectl logs POD_NAME -n ironpass                  # 4. what did the app print?
kubectl logs POD_NAME -n ironpass --previous       #    ... before it crashed?
kubectl get endpoints -n ironpass                  # 5. does the Service have pods behind it?
kubectl get pods -n ironpass --show-labels         # 6. do the pod labels match the selector?
```

The three labs below are in `troubleshooting/`. Apply a file with `kubectl apply -f FILE`,
and fix it by editing the file and applying it again. Do not patch live objects by hand.

## Lab 1: ImagePullBackOff (the image does not exist)

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n ironpass -l lab=broken-image
kubectl describe pod -n ironpass -l lab=broken-image
kubectl get events -n ironpass --sort-by=.lastTimestamp
```

What you see: the status goes `ErrImagePull`, then `ImagePullBackOff`. The Events say
`manifest unknown` for the tag `v9.9.9-does-not-exist`.

Why: Kubernetes asked GHCR for an image tag that was never pushed.

Fix: change the `image:` line in `troubleshooting/broken-image.yaml` to a tag that exists
(a commit SHA the pipeline pushed), then apply the file again.

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl rollout status deployment/ironpass-broken-image -n ironpass
kubectl get pods -n ironpass -l lab=broken-image
```

## Lab 2: Service with no endpoints (labels do not match)

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get pods -n ironpass --show-labels -l lab=broken-service
kubectl get svc,endpoints -n ironpass ironpass-broken-service
kubectl describe svc ironpass-broken-service -n ironpass
```

What you see: the pod is `Running` and `READY 1/1`, but the endpoints list is `<none>`.
The Service selector says `tier=webb` and the pod label says `tier=web`.

Why: a Service only sends traffic to pods whose labels match its selector exactly.

Fix: change `tier: webb` to `tier: web` in `troubleshooting/broken-service.yaml`, apply again.

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get endpoints -n ironpass ironpass-broken-service
```

## Lab 3: CrashLoopBackOff (the container keeps exiting)

```bash
kubectl apply -f troubleshooting/broken-crashloop.yaml
kubectl get pods -n ironpass -l lab=broken-crashloop
kubectl describe pod -n ironpass -l lab=broken-crashloop
kubectl logs -n ironpass -l lab=broken-crashloop --previous
```

What you see: the status flips between `Error` and `CrashLoopBackOff`, and `RESTARTS` keeps
going up. `describe` shows `Last State: Terminated` with `Exit Code: 1`. The log says
`fatal: environment variable DB_HOST is not set`.

Why: the container did start (so the image is fine), but the program stopped itself
because a setting is missing. Kubernetes restarts it again and again, waiting longer each time.

Fix: give the container the missing variable. In `troubleshooting/broken-crashloop.yaml`
remove the `#` in front of the `env:` lines, then apply again.

```bash
kubectl apply -f troubleshooting/broken-crashloop.yaml
kubectl get pods -n ironpass -l lab=broken-crashloop
kubectl logs -n ironpass -l lab=broken-crashloop
```

## Clean up

```bash
kubectl delete -f troubleshooting/
```

## Cheat sheet

| What you see | First thing to check |
| --- | --- |
| `Pending` | `describe pod`, look for "Insufficient cpu" or an unbound PVC |
| `ImagePullBackOff` | the image name and tag in the Deployment, `describe pod` Events |
| `CrashLoopBackOff` | `logs --previous`, then the exit code in `describe pod` |
| `Running` but not `Ready` | the readiness probe path and port, `describe pod` Events |
| Service answers nothing | `get endpoints`, then `get pods --show-labels` against the selector |
| Ingress gives 404 or 502 | `describe ingress`, then the backend Service name and port |

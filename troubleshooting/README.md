# Troubleshooting lab

Two small manifests that are broken on purpose. Both go into the `ironpass`
namespace and do not touch the real app.

## Lab 1: broken image

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n ironpass -l lab=broken-image
kubectl describe pod -n ironpass -l lab=broken-image
kubectl get events -n ironpass --sort-by=.lastTimestamp | tail
```

What you see: the pod is stuck in `ErrImagePull`, then `ImagePullBackOff`.
The events say the manifest for tag `v9.9.9-does-not-exist` was not found.

Fix: point the Deployment at a tag that exists, for example a commit SHA that
the pipeline pushed.

```bash
kubectl set image deployment/ironpass-broken-image -n ironpass \
  backend=ghcr.io/brixdorf/ironpass-backend:<a-real-sha>
kubectl rollout status deployment/ironpass-broken-image -n ironpass
```

## Lab 2: broken service

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get pods -n ironpass --show-labels -l lab=broken-service
kubectl get svc,endpoints -n ironpass ironpass-broken-service
kubectl describe svc -n ironpass ironpass-broken-service
```

What you see: the pod is `Running` but the endpoints list is `<none>`.
The Service selector is `tier=webb`, the pod label is `tier=web`.
A Service only sends traffic to pods whose labels match its selector.

Fix: correct the selector.

```bash
kubectl patch svc ironpass-broken-service -n ironpass \
  -p '{"spec":{"selector":{"tier":"web"}}}'
kubectl get endpoints -n ironpass ironpass-broken-service
```

## Clean up

```bash
kubectl delete -f troubleshooting/
```

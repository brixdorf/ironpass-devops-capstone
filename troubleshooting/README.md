# Troubleshooting lab

Three manifests that are broken on purpose. They go into the `ironpass`
namespace and do not touch the real app.

| File | Symptom | Cause |
| --- | --- | --- |
| `broken-image.yaml` | `ImagePullBackOff` | the image tag does not exist |
| `broken-service.yaml` | pod `Running`, Service has no endpoints | selector `tier: webb` does not match label `tier: web` |
| `broken-crashloop.yaml` | `CrashLoopBackOff` | the container exits because `DB_HOST` is not set |

The exact diagnosis steps and the fixes are in [docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md).

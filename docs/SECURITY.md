# Security scan

Trivy scans both container images (backend and frontend) in the pipeline,
looking for HIGH and CRITICAL vulnerabilities in the operating system packages
and in the Python and Node libraries inside each image, and it fails the build
only when a fix already exists. The first runs of the pipeline failed on
purpose: the backend image had 7 HIGH findings (old `starlette` and a bundled
`urllib3`, `msgpack` and `setuptools`) and the frontend image had 41 findings
in old Alpine packages such as `openssl` (2 CRITICAL, 39 HIGH). I fixed them by
upgrading the Python dependencies, removing `pip` and `setuptools` from the
runtime image, and moving to a current `nginx-unprivileged` base image, and
after that both scans came back clean and the images were pushed.

A clean result means no known and fixable HIGH or CRITICAL issue at the time of
the scan. It does not prove the images are safe forever, because new CVEs are
published every day, so the scan runs again on every push.

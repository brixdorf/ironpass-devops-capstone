import time

from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

REQUESTS = Counter(
    "ironpass_http_requests_total",
    "Total HTTP requests handled by the API",
    ["method", "path", "status"],
)
LATENCY = Histogram(
    "ironpass_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
IN_PROGRESS = Gauge(
    "ironpass_http_requests_in_progress",
    "Requests being handled right now",
)
CHECKINS = Counter(
    "ironpass_checkins_total",
    "Check-in attempts by result",
    ["result"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        start = time.perf_counter()
        IN_PROGRESS.inc()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            IN_PROGRESS.dec()
            route = request.scope.get("route")
            # use the route template so ids do not explode the label count
            path = route.path if route is not None else "unmatched"
            REQUESTS.labels(request.method, path, str(status)).inc()
            LATENCY.labels(request.method, path).observe(time.perf_counter() - start)

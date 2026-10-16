from app.db import get_db
from app.main import app


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_ready_returns_503_when_database_is_down(client):
    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise RuntimeError("connection refused")

    app.dependency_overrides[get_db] = lambda: BrokenSession()
    response = client.get("/ready")
    assert response.status_code == 503


def test_metrics_in_prometheus_format(client):
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "# HELP" in response.text
    assert "ironpass_http_requests_total" in response.text

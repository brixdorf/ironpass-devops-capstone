def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_metrics_in_prometheus_format(client):
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "ironpass_http_requests_total" in response.text
    assert "# HELP" in response.text


def test_create_and_list_plans(client):
    created = client.post(
        "/api/plans",
        json={"name": "Annual", "price_cents": 30000, "duration_days": 365},
    )
    assert created.status_code == 201
    names = [p["name"] for p in client.get("/api/plans").json()]
    assert "Annual" in names


def test_duplicate_plan_name_is_rejected(client, plan):
    response = client.post(
        "/api/plans",
        json={"name": "Monthly", "price_cents": 100, "duration_days": 10},
    )
    assert response.status_code == 409


def test_create_member_sets_expiry_from_plan(client, plan):
    response = client.post(
        "/api/members",
        json={"full_name": "Asha Verma", "email": "asha@example.com", "plan_id": plan.id},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["effective_status"] == "active"
    assert body["plan_name"] == "Monthly"
    assert body["expires_on"] > body["joined_on"]


def test_create_member_with_unknown_plan_returns_404(client):
    response = client.post(
        "/api/members",
        json={"full_name": "Asha Verma", "email": "asha@example.com", "plan_id": 999},
    )
    assert response.status_code == 404


def test_duplicate_email_is_rejected(client, make_member, plan):
    make_member(email="dup@example.com")
    response = client.post(
        "/api/members",
        json={"full_name": "Other Person", "email": "dup@example.com", "plan_id": plan.id},
    )
    assert response.status_code == 409


def test_get_missing_member_returns_404(client):
    assert client.get("/api/members/12345").status_code == 404


def test_update_member_status(client, make_member):
    member_id = make_member()
    response = client.put(f"/api/members/{member_id}", json={"status": "frozen"})
    assert response.status_code == 200
    assert response.json()["effective_status"] == "frozen"


def test_delete_member(client, make_member):
    member_id = make_member()
    assert client.delete(f"/api/members/{member_id}").status_code == 204
    assert client.get(f"/api/members/{member_id}").status_code == 404


def test_filter_members_by_status(client, make_member):
    make_member(email="live@example.com", expires_in_days=20)
    make_member(email="old@example.com", expires_in_days=-5)
    expired = client.get("/api/members", params={"status": "expired"}).json()
    assert [m["email"] for m in expired] == ["old@example.com"]


def test_checkin_accepted_for_active_member(client, make_member):
    member_id = make_member(expires_in_days=10)
    response = client.post("/api/checkins", json={"member_id": member_id})
    assert response.status_code == 201
    assert response.json()["member_id"] == member_id
    assert len(client.get("/api/checkins").json()) == 1


def test_checkin_rejected_when_plan_expired(client, make_member):
    member_id = make_member(expires_in_days=-1)
    response = client.post("/api/checkins", json={"member_id": member_id})
    assert response.status_code == 409
    assert "expired" in response.json()["detail"]
    assert client.get("/api/checkins").json() == []


def test_checkin_rejected_when_member_frozen(client, make_member):
    member_id = make_member(status="frozen")
    response = client.post("/api/checkins", json={"member_id": member_id})
    assert response.status_code == 409


def test_renew_lets_expired_member_check_in_again(client, make_member):
    member_id = make_member(expires_in_days=-10)
    assert client.post("/api/checkins", json={"member_id": member_id}).status_code == 409
    renewed = client.post(f"/api/members/{member_id}/renew")
    assert renewed.status_code == 200
    assert renewed.json()["effective_status"] == "active"
    assert client.post("/api/checkins", json={"member_id": member_id}).status_code == 201


def test_stats_counts_members(client, make_member):
    make_member(email="a@example.com", expires_in_days=30)
    make_member(email="b@example.com", expires_in_days=-3)
    stats = client.get("/api/stats").json()
    assert stats["total_members"] == 2
    assert stats["active_members"] == 1
    assert stats["expired_members"] == 1

def test_checkin_accepted_for_active_member(client, make_member):
    member_id = make_member(expires_in_days=10)
    response = client.post("/api/checkins", json={"member_id": member_id})
    assert response.status_code == 201
    assert response.json()["member_id"] == member_id
    assert len(client.get("/api/checkins").json()) == 1


def test_checkin_rejected_when_plan_expired(client, make_member):
    """The business rule: an expired plan cannot check in."""
    member_id = make_member(expires_in_days=-1)
    response = client.post("/api/checkins", json={"member_id": member_id})
    assert response.status_code == 409
    assert "EXPIRED" in response.json()["detail"]
    assert client.get("/api/checkins").json() == []


def test_checkin_rejected_when_member_frozen(client, make_member):
    member_id = make_member(status="FROZEN")
    response = client.post("/api/checkins", json={"member_id": member_id})
    assert response.status_code == 409
    assert "FROZEN" in response.json()["detail"]


def test_checkin_for_unknown_member_returns_404(client):
    assert client.post("/api/checkins", json={"member_id": 4242}).status_code == 404


def test_checkin_without_member_id_returns_422(client):
    assert client.post("/api/checkins", json={}).status_code == 422


def test_renew_lets_expired_member_check_in_again(client, make_member):
    member_id = make_member(expires_in_days=-10)
    assert client.post("/api/checkins", json={"member_id": member_id}).status_code == 409
    renewed = client.post(f"/api/members/{member_id}/renew")
    assert renewed.status_code == 200
    assert renewed.json()["effective_status"] == "ACTIVE"
    assert client.post("/api/checkins", json={"member_id": member_id}).status_code == 201


def test_cancelled_member_cannot_be_renewed(client, make_member):
    member_id = make_member(status="CANCELLED")
    assert client.post(f"/api/members/{member_id}/renew").status_code == 409

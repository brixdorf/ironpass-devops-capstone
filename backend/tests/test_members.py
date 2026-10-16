def test_create_member_sets_expiry_from_plan(client, plan):
    response = client.post(
        "/api/members",
        json={"full_name": "Asha Verma", "email": "asha@example.com", "plan_id": plan.id},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ACTIVE"
    assert body["effective_status"] == "ACTIVE"
    assert body["plan_name"] == "Monthly"
    assert body["expires_on"] > body["joined_on"]


def test_create_member_with_unknown_plan_returns_404(client):
    response = client.post(
        "/api/members",
        json={"full_name": "Asha Verma", "email": "asha@example.com", "plan_id": 999},
    )
    assert response.status_code == 404


def test_create_member_with_bad_email_returns_422(client, plan):
    response = client.post(
        "/api/members",
        json={"full_name": "Asha Verma", "email": "not-an-email", "plan_id": plan.id},
    )
    assert response.status_code == 422


def test_duplicate_email_is_rejected(client, make_member, plan):
    make_member(email="dup@example.com")
    response = client.post(
        "/api/members",
        json={"full_name": "Other Person", "email": "dup@example.com", "plan_id": plan.id},
    )
    assert response.status_code == 409


def test_get_missing_member_returns_404(client):
    response = client.get("/api/members/12345")
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"


def test_update_member_status(client, make_member):
    member_id = make_member()
    response = client.put(f"/api/members/{member_id}", json={"status": "FROZEN"})
    assert response.status_code == 200
    assert response.json()["effective_status"] == "FROZEN"


def test_status_must_be_one_of_the_allowed_values(client, make_member):
    member_id = make_member()
    assert client.put(f"/api/members/{member_id}", json={"status": "PAUSED"}).status_code == 422
    assert client.put(f"/api/members/{member_id}", json={"status": "frozen"}).status_code == 422
    # EXPIRED is worked out from the date, staff cannot set it
    assert client.put(f"/api/members/{member_id}", json={"status": "EXPIRED"}).status_code == 422


def test_update_missing_member_returns_404(client):
    assert client.put("/api/members/777", json={"status": "FROZEN"}).status_code == 404


def test_delete_member(client, make_member):
    member_id = make_member()
    assert client.delete(f"/api/members/{member_id}").status_code == 204
    assert client.get(f"/api/members/{member_id}").status_code == 404


def test_filter_members_by_status(client, make_member):
    make_member(email="live@example.com", expires_in_days=20)
    make_member(email="old@example.com", expires_in_days=-5)
    expired = client.get("/api/members", params={"status": "EXPIRED"}).json()
    assert [m["email"] for m in expired] == ["old@example.com"]


def test_filter_with_unknown_status_returns_422(client):
    assert client.get("/api/members", params={"status": "BANANA"}).status_code == 422

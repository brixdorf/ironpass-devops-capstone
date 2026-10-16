def test_create_and_list_plans(client):
    created = client.post(
        "/api/plans",
        json={"name": "Annual", "plan_type": "ANNUAL", "price_cents": 30000, "duration_days": 365},
    )
    assert created.status_code == 201
    assert created.json()["plan_type"] == "ANNUAL"
    names = [p["name"] for p in client.get("/api/plans").json()]
    assert "Annual" in names


def test_wrong_plan_type_returns_422(client):
    response = client.post(
        "/api/plans",
        json={"name": "Weekly", "plan_type": "WEEKLY", "price_cents": 1000, "duration_days": 7},
    )
    assert response.status_code == 422


def test_plan_type_must_be_capital_letters(client):
    response = client.post(
        "/api/plans",
        json={"name": "Monthly", "plan_type": "monthly", "price_cents": 1000, "duration_days": 30},
    )
    assert response.status_code == 422


def test_negative_price_returns_422(client):
    response = client.post(
        "/api/plans",
        json={"name": "Odd", "plan_type": "MONTHLY", "price_cents": -5, "duration_days": 30},
    )
    assert response.status_code == 422


def test_duplicate_plan_name_is_rejected(client, plan):
    response = client.post(
        "/api/plans",
        json={"name": "Monthly", "plan_type": "MONTHLY", "price_cents": 100, "duration_days": 10},
    )
    assert response.status_code == 409

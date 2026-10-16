def test_stats_counts_members(client, make_member):
    make_member(email="a@example.com", expires_in_days=30)
    make_member(email="b@example.com", expires_in_days=-3)
    make_member(email="c@example.com", status="FROZEN")
    stats = client.get("/api/stats").json()
    assert stats["total_members"] == 3
    assert stats["active_members"] == 1
    assert stats["expired_members"] == 1
    assert stats["frozen_members"] == 1


def test_stats_counts_checkins_today_and_expiring_soon(client, make_member):
    soon = make_member(email="soon@example.com", expires_in_days=3)
    make_member(email="later@example.com", expires_in_days=40)
    client.post("/api/checkins", json={"member_id": soon})
    stats = client.get("/api/stats").json()
    assert stats["check_ins_today"] == 1
    assert stats["expiring_soon"] == 1


def test_activity_feed_mixes_signups_and_checkins(client, plan):
    created = client.post(
        "/api/members",
        json={"full_name": "Asha Verma", "email": "asha@example.com", "plan_id": plan.id},
    ).json()
    client.post("/api/checkins", json={"member_id": created["id"]})
    feed = client.get("/api/activity").json()
    assert [item["type"] for item in feed] == ["CHECKIN", "SIGNUP"]
    assert feed[0]["message"] == "Asha Verma checked in"
    assert feed[1]["message"] == "Asha Verma joined on Monthly"


def test_activity_feed_is_empty_on_a_new_database(client):
    assert client.get("/api/activity").json() == []


def test_activity_limit_is_validated(client):
    assert client.get("/api/activity", params={"limit": 0}).status_code == 422

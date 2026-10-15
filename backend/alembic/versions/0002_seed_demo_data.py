"""seed demo plans, members and check-ins

Revision ID: 0002
Revises: 0001
Create Date: 2025-01-10 09:05:00
"""
from datetime import date, datetime, timedelta, timezone

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

# (name, price in cents, duration in days)
PLANS = [
    ("Day Pass", 800, 1),
    ("Monthly", 3500, 30),
    ("Quarterly", 9000, 90),
    ("Annual", 30000, 365),
]

# (full name, email, plan name, joined days ago, days until expiry, status)
MEMBERS = [
    ("Aarav Mehta", "aarav.mehta@example.com", "Annual", 120, 245, "active"),
    ("Diya Nair", "diya.nair@example.com", "Monthly", 20, 10, "active"),
    ("Kabir Singh", "kabir.singh@example.com", "Quarterly", 80, 10, "active"),
    ("Isha Kapoor", "isha.kapoor@example.com", "Monthly", 50, -20, "active"),
    ("Rohan Das", "rohan.das@example.com", "Monthly", 33, -3, "active"),
    ("Meera Iyer", "meera.iyer@example.com", "Annual", 200, 165, "frozen"),
    ("Vikram Rao", "vikram.rao@example.com", "Quarterly", 10, 80, "active"),
    ("Anika Bose", "anika.bose@example.com", "Day Pass", 0, 1, "active"),
]

CHECK_INS = [
    ("aarav.mehta@example.com", 0),
    ("diya.nair@example.com", 0),
    ("vikram.rao@example.com", 1),
    ("aarav.mehta@example.com", 2),
]


def upgrade() -> None:
    conn = op.get_bind()
    today = date.today()
    now = datetime.now(timezone.utc)

    for name, price, days in PLANS:
        conn.execute(
            sa.text(
                "INSERT INTO plans (name, price_cents, duration_days) "
                "VALUES (:name, :price, :days)"
            ),
            {"name": name, "price": price, "days": days},
        )

    for full_name, email, plan, joined_ago, left, status in MEMBERS:
        conn.execute(
            sa.text(
                "INSERT INTO members (full_name, email, plan_id, status, joined_on, expires_on) "
                "VALUES (:full_name, :email, (SELECT id FROM plans WHERE name = :plan), "
                ":status, :joined, :expires)"
            ),
            {
                "full_name": full_name,
                "email": email,
                "plan": plan,
                "status": status,
                "joined": today - timedelta(days=joined_ago),
                "expires": today + timedelta(days=left),
            },
        )

    for email, days_ago in CHECK_INS:
        conn.execute(
            sa.text(
                "INSERT INTO check_ins (member_id, checked_in_at) "
                "VALUES ((SELECT id FROM members WHERE email = :email), :at)"
            ),
            {"email": email, "at": now - timedelta(days=days_ago, minutes=days_ago * 7)},
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM check_ins"))
    conn.execute(sa.text("DELETE FROM members"))
    conn.execute(sa.text("DELETE FROM plans"))

"""add plan types, add created_at, make statuses capital letters

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-16 09:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

PLAN_TYPES = {
    "Day Pass": "DAY_PASS",
    "Monthly": "MONTHLY",
    "Quarterly": "QUARTERLY",
    "Annual": "ANNUAL",
}


def upgrade() -> None:
    conn = op.get_bind()

    # plans get a type, existing rows are filled from their name
    op.add_column(
        "plans",
        sa.Column("plan_type", sa.String(20), nullable=False, server_default="MONTHLY"),
    )
    for name, plan_type in PLAN_TYPES.items():
        conn.execute(
            sa.text("UPDATE plans SET plan_type = :t WHERE name = :n"),
            {"t": plan_type, "n": name},
        )

    # member statuses become ACTIVE, FROZEN, CANCELLED
    conn.execute(sa.text("UPDATE members SET status = UPPER(status)"))
    op.alter_column("members", "status", server_default="ACTIVE")

    # signups need a time stamp for the activity feed
    op.add_column(
        "members",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    conn.execute(sa.text("UPDATE members SET created_at = joined_on"))


def downgrade() -> None:
    conn = op.get_bind()
    op.drop_column("members", "created_at")
    conn.execute(sa.text("UPDATE members SET status = LOWER(status)"))
    op.alter_column("members", "status", server_default="active")
    op.drop_column("plans", "plan_type")

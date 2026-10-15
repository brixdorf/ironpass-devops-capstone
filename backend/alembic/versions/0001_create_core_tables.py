"""create plans, members and check_ins

Revision ID: 0001
Revises:
Create Date: 2025-01-10 09:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(60), nullable=False, unique=True),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
    )
    op.create_table(
        "members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(160), nullable=False, unique=True),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("joined_on", sa.Date(), nullable=False),
        sa.Column("expires_on", sa.Date(), nullable=False),
    )
    op.create_index("ix_members_plan_id", "members", ["plan_id"])
    op.create_table(
        "check_ins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("member_id", sa.Integer(), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_check_ins_member_id", "check_ins", ["member_id"])


def downgrade() -> None:
    op.drop_table("check_ins")
    op.drop_table("members")
    op.drop_table("plans")

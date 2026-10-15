from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True)
    price_cents: Mapped[int] = mapped_column(Integer)
    duration_days: Mapped[int] = mapped_column(Integer)

    members: Mapped[list["Member"]] = relationship(back_populates="plan")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    # active, frozen or cancelled. Expiry is decided by expires_on.
    status: Mapped[str] = mapped_column(String(20), default="active")
    joined_on: Mapped[date] = mapped_column(Date)
    expires_on: Mapped[date] = mapped_column(Date)

    plan: Mapped[Plan] = relationship(back_populates="members")
    check_ins: Mapped[list["CheckIn"]] = relationship(
        back_populates="member", cascade="all, delete-orphan"
    )


class CheckIn(Base):
    __tablename__ = "check_ins"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    checked_in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    member: Mapped[Member] = relationship(back_populates="check_ins")

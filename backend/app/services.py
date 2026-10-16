"""Business rules. The routers call these so the rules live in one place."""

from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.enums import MemberStatus


def today() -> date:
    return date.today()


def effective_status(member: models.Member) -> MemberStatus:
    """The status the gym actually applies. A past expiry date wins over ACTIVE."""
    if member.status in (MemberStatus.CANCELLED.value, MemberStatus.FROZEN.value):
        return MemberStatus(member.status)
    if member.expires_on < today():
        return MemberStatus.EXPIRED
    return MemberStatus.ACTIVE


def ensure_can_check_in(member: models.Member) -> None:
    """Business rule: only members with a valid ACTIVE plan may enter the gym."""
    state = effective_status(member)
    if state != MemberStatus.ACTIVE:
        raise HTTPException(
            status_code=409,
            detail=f"Check-in rejected, membership is {state.value}",
        )


def member_out(member: models.Member) -> schemas.MemberOut:
    return schemas.MemberOut(
        id=member.id,
        full_name=member.full_name,
        email=member.email,
        plan_id=member.plan_id,
        plan_name=member.plan.name,
        plan_type=member.plan.plan_type,
        status=member.status,
        effective_status=effective_status(member),
        joined_on=member.joined_on,
        expires_on=member.expires_on,
    )


def get_member_or_404(db: Session, member_id: int) -> models.Member:
    member = db.get(models.Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


def get_plan_or_404(db: Session, plan_id: int) -> models.Plan:
    plan = db.get(models.Plan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

from datetime import timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.db import get_db
from app.enums import ActivityType, MemberStatus
from app.services import effective_status, today

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/stats", response_model=schemas.Stats)
def stats(db: Session = Depends(get_db)):
    members = db.scalars(select(models.Member)).all()
    states = [effective_status(m) for m in members]
    soon = today() + timedelta(days=settings.expiring_soon_days)
    checked_in_today = func.date(models.CheckIn.checked_in_at) == today()
    check_ins_today = db.scalar(select(func.count(models.CheckIn.id)).where(checked_in_today))
    return schemas.Stats(
        total_members=len(members),
        active_members=states.count(MemberStatus.ACTIVE),
        expired_members=states.count(MemberStatus.EXPIRED),
        frozen_members=states.count(MemberStatus.FROZEN),
        check_ins_today=check_ins_today or 0,
        expiring_soon=sum(
            1
            for m, s in zip(members, states)
            if s == MemberStatus.ACTIVE and m.expires_on <= soon
        ),
    )


@router.get("/activity", response_model=list[schemas.ActivityOut])
def recent_activity(limit: int = Query(default=10, ge=1, le=50), db: Session = Depends(get_db)):
    """Newest check-ins and signups together. The front desk feed reads this."""
    check_ins = db.scalars(
        select(models.CheckIn).order_by(models.CheckIn.checked_in_at.desc()).limit(limit)
    ).all()
    signups = db.scalars(
        select(models.Member).order_by(models.Member.created_at.desc()).limit(limit)
    ).all()

    items = [
        schemas.ActivityOut(
            type=ActivityType.CHECKIN,
            member_id=c.member_id,
            member_name=c.member.full_name,
            message=f"{c.member.full_name} checked in",
            at=c.checked_in_at,
        )
        for c in check_ins
    ] + [
        schemas.ActivityOut(
            type=ActivityType.SIGNUP,
            member_id=m.id,
            member_name=m.full_name,
            message=f"{m.full_name} joined on {m.plan.name}",
            at=m.created_at,
        )
        for m in signups
    ]
    items.sort(key=lambda item: item.at, reverse=True)
    return items[:limit]

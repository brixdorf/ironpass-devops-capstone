from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.enums import MemberStatus
from app.services import (
    get_member_or_404,
    get_plan_or_404,
    member_out,
    today,
)

router = APIRouter(prefix="/api/members", tags=["members"])


@router.get("", response_model=list[schemas.MemberOut])
def list_members(
    plan_id: Optional[int] = None,
    status: Optional[MemberStatus] = None,
    db: Session = Depends(get_db),
):
    query = select(models.Member).order_by(models.Member.full_name)
    if plan_id is not None:
        query = query.where(models.Member.plan_id == plan_id)
    members = [member_out(m) for m in db.scalars(query).all()]
    if status is not None:
        members = [m for m in members if m.effective_status == status]
    return members


@router.get("/{member_id}", response_model=schemas.MemberOut)
def get_member(member_id: int, db: Session = Depends(get_db)):
    return member_out(get_member_or_404(db, member_id))


@router.post("", response_model=schemas.MemberOut, status_code=201)
def create_member(body: schemas.MemberCreate, db: Session = Depends(get_db)):
    plan = get_plan_or_404(db, body.plan_id)
    if db.scalar(select(models.Member).where(models.Member.email == body.email)):
        raise HTTPException(status_code=409, detail="This email is already registered")
    start = today()
    member = models.Member(
        full_name=body.full_name,
        email=body.email,
        plan_id=plan.id,
        status=MemberStatus.ACTIVE.value,
        joined_on=start,
        expires_on=start + timedelta(days=plan.duration_days),
    )
    db.add(member)
    db.commit()
    return member_out(member)


@router.put("/{member_id}", response_model=schemas.MemberOut)
def update_member(member_id: int, body: schemas.MemberUpdate, db: Session = Depends(get_db)):
    member = get_member_or_404(db, member_id)
    changes = body.model_dump(exclude_unset=True, mode="json")
    if changes.get("plan_id") is not None:
        get_plan_or_404(db, changes["plan_id"])
    for field, value in changes.items():
        if value is not None:
            setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return member_out(member)


@router.post("/{member_id}/renew", response_model=schemas.MemberOut)
def renew_member(member_id: int, db: Session = Depends(get_db)):
    member = get_member_or_404(db, member_id)
    if member.status == MemberStatus.CANCELLED.value:
        raise HTTPException(status_code=409, detail="CANCELLED members cannot be renewed")
    base = max(member.expires_on, today())
    member.expires_on = base + timedelta(days=member.plan.duration_days)
    db.commit()
    return member_out(member)


@router.delete("/{member_id}", status_code=204)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member = get_member_or_404(db, member_id)
    db.delete(member)
    db.commit()
    return Response(status_code=204)

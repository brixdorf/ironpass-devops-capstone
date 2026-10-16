from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.metrics import CHECKINS
from app.services import ensure_can_check_in, get_member_or_404

router = APIRouter(prefix="/api/checkins", tags=["check-ins"])


def checkin_out(row: models.CheckIn) -> schemas.CheckInOut:
    return schemas.CheckInOut(
        id=row.id,
        member_id=row.member_id,
        member_name=row.member.full_name,
        checked_in_at=row.checked_in_at,
    )


@router.post("", response_model=schemas.CheckInOut, status_code=201)
def create_checkin(body: schemas.CheckInCreate, db: Session = Depends(get_db)):
    member = get_member_or_404(db, body.member_id)
    try:
        ensure_can_check_in(member)
    except HTTPException:
        CHECKINS.labels("rejected").inc()
        raise
    entry = models.CheckIn(member_id=member.id)
    db.add(entry)
    db.commit()
    CHECKINS.labels("accepted").inc()
    return checkin_out(entry)


@router.get("", response_model=list[schemas.CheckInOut])
def list_checkins(limit: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(models.CheckIn).order_by(models.CheckIn.checked_in_at.desc()).limit(limit)
    ).all()
    return [checkin_out(r) for r in rows]

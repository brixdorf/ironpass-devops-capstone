from datetime import date, timedelta

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.metrics import CHECKINS, MetricsMiddleware

app = FastAPI(title="IronPass API", version="1.0.0")
app.add_middleware(MetricsMiddleware)

EXPIRING_SOON_DAYS = 7


def today() -> date:
    return date.today()


def effective_status(member: models.Member) -> str:
    """Status the gym actually applies. A past expiry date wins over 'active'."""
    if member.status in ("cancelled", "frozen"):
        return member.status
    if member.expires_on < today():
        return "expired"
    return "active"


def member_out(member: models.Member) -> schemas.MemberOut:
    return schemas.MemberOut(
        id=member.id,
        full_name=member.full_name,
        email=member.email,
        plan_id=member.plan_id,
        plan_name=member.plan.name,
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


# ---- service endpoints ----


@app.get("/")
def root():
    return {"service": "ironpass-api", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="database not reachable")
    return {"status": "ready"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ---- plans ----


@app.get("/api/plans", response_model=list[schemas.PlanOut])
def list_plans(db: Session = Depends(get_db)):
    return db.scalars(select(models.Plan).order_by(models.Plan.price_cents)).all()


@app.post("/api/plans", response_model=schemas.PlanOut, status_code=201)
def create_plan(body: schemas.PlanCreate, db: Session = Depends(get_db)):
    if db.scalar(select(models.Plan).where(models.Plan.name == body.name)):
        raise HTTPException(status_code=409, detail="A plan with this name already exists")
    plan = models.Plan(**body.model_dump())
    db.add(plan)
    db.commit()
    return plan


# ---- members ----


@app.get("/api/members", response_model=list[schemas.MemberOut])
def list_members(
    plan_id: int | None = None,
    status: str | None = Query(default=None, pattern="^(active|expired|frozen|cancelled)$"),
    db: Session = Depends(get_db),
):
    query = select(models.Member).order_by(models.Member.full_name)
    if plan_id is not None:
        query = query.where(models.Member.plan_id == plan_id)
    members = [member_out(m) for m in db.scalars(query).all()]
    if status:
        members = [m for m in members if m.effective_status == status]
    return members


@app.get("/api/members/{member_id}", response_model=schemas.MemberOut)
def get_member(member_id: int, db: Session = Depends(get_db)):
    return member_out(get_member_or_404(db, member_id))


@app.post("/api/members", response_model=schemas.MemberOut, status_code=201)
def create_member(body: schemas.MemberCreate, db: Session = Depends(get_db)):
    plan = get_plan_or_404(db, body.plan_id)
    if db.scalar(select(models.Member).where(models.Member.email == body.email)):
        raise HTTPException(status_code=409, detail="This email is already registered")
    start = today()
    member = models.Member(
        full_name=body.full_name,
        email=body.email,
        plan_id=plan.id,
        status="active",
        joined_on=start,
        expires_on=start + timedelta(days=plan.duration_days),
    )
    db.add(member)
    db.commit()
    return member_out(member)


@app.put("/api/members/{member_id}", response_model=schemas.MemberOut)
def update_member(member_id: int, body: schemas.MemberUpdate, db: Session = Depends(get_db)):
    member = get_member_or_404(db, member_id)
    changes = body.model_dump(exclude_unset=True)
    if "plan_id" in changes and changes["plan_id"] is not None:
        get_plan_or_404(db, changes["plan_id"])
    for field, value in changes.items():
        if value is not None:
            setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return member_out(member)


@app.post("/api/members/{member_id}/renew", response_model=schemas.MemberOut)
def renew_member(member_id: int, db: Session = Depends(get_db)):
    member = get_member_or_404(db, member_id)
    if member.status == "cancelled":
        raise HTTPException(status_code=409, detail="Cancelled members cannot be renewed")
    base = max(member.expires_on, today())
    member.expires_on = base + timedelta(days=member.plan.duration_days)
    db.commit()
    return member_out(member)


@app.delete("/api/members/{member_id}", status_code=204)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member = get_member_or_404(db, member_id)
    db.delete(member)
    db.commit()
    return Response(status_code=204)


# ---- check-ins ----


@app.post("/api/checkins", response_model=schemas.CheckInOut, status_code=201)
def create_checkin(body: schemas.CheckInCreate, db: Session = Depends(get_db)):
    member = get_member_or_404(db, body.member_id)
    state = effective_status(member)
    # business rule: only members with a valid, active plan may enter the gym
    if state != "active":
        CHECKINS.labels("rejected").inc()
        raise HTTPException(
            status_code=409,
            detail=f"Check-in rejected, membership is {state}",
        )
    entry = models.CheckIn(member_id=member.id)
    db.add(entry)
    db.commit()
    CHECKINS.labels("accepted").inc()
    return schemas.CheckInOut(
        id=entry.id,
        member_id=member.id,
        member_name=member.full_name,
        checked_in_at=entry.checked_in_at,
    )


@app.get("/api/checkins", response_model=list[schemas.CheckInOut])
def list_checkins(limit: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(models.CheckIn).order_by(models.CheckIn.checked_in_at.desc()).limit(limit)
    ).all()
    return [
        schemas.CheckInOut(
            id=r.id,
            member_id=r.member_id,
            member_name=r.member.full_name,
            checked_in_at=r.checked_in_at,
        )
        for r in rows
    ]


# ---- stats ----


@app.get("/api/stats", response_model=schemas.Stats)
def stats(db: Session = Depends(get_db)):
    members = db.scalars(select(models.Member)).all()
    states = [effective_status(m) for m in members]
    soon = today() + timedelta(days=EXPIRING_SOON_DAYS)
    start_of_day = func.date(models.CheckIn.checked_in_at) == today()
    check_ins_today = db.scalar(select(func.count(models.CheckIn.id)).where(start_of_day))
    return schemas.Stats(
        total_members=len(members),
        active_members=states.count("active"),
        expired_members=states.count("expired"),
        frozen_members=states.count("frozen"),
        check_ins_today=check_ins_today or 0,
        expiring_soon=sum(
            1
            for m, s in zip(members, states)
            if s == "active" and m.expires_on <= soon
        ),
    )

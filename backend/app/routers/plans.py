from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.get("", response_model=list[schemas.PlanOut])
def list_plans(db: Session = Depends(get_db)):
    return db.scalars(select(models.Plan).order_by(models.Plan.price_cents)).all()


@router.post("", response_model=schemas.PlanOut, status_code=201)
def create_plan(body: schemas.PlanCreate, db: Session = Depends(get_db)):
    if db.scalar(select(models.Plan).where(models.Plan.name == body.name)):
        raise HTTPException(status_code=409, detail="A plan with this name already exists")
    plan = models.Plan(**body.model_dump(mode="json"))
    db.add(plan)
    db.commit()
    return plan

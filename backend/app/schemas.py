from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.enums import ActivityType, MemberStatus, PlanType, StoredStatus


class PlanCreate(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    plan_type: PlanType
    price_cents: int = Field(gt=0)
    duration_days: int = Field(gt=0)


class PlanOut(PlanCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class MemberCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    plan_id: int


class MemberUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    plan_id: Optional[int] = None
    status: Optional[StoredStatus] = None


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: str
    plan_id: int
    plan_name: str
    plan_type: PlanType
    status: StoredStatus
    effective_status: MemberStatus
    joined_on: date
    expires_on: date


class CheckInCreate(BaseModel):
    member_id: int


class CheckInOut(BaseModel):
    id: int
    member_id: int
    member_name: str
    checked_in_at: datetime


class ActivityOut(BaseModel):
    type: ActivityType
    member_id: int
    member_name: str
    message: str
    at: datetime


class Stats(BaseModel):
    total_members: int
    active_members: int
    expired_members: int
    frozen_members: int
    check_ins_today: int
    expiring_soon: int

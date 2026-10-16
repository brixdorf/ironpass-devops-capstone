from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.db import Base, get_db
from app.enums import MemberStatus, PlanType
from app.main import app


@pytest.fixture()
def session_factory():
    """A fresh in-memory SQLite database for every test.

    The real app never calls create_all, its tables come from Alembic.
    Tests are the one place that builds tables directly, on SQLite.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    yield factory
    engine.dispose()


@pytest.fixture()
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def plan(session_factory):
    with session_factory() as db:
        p = models.Plan(
            name="Monthly",
            plan_type=PlanType.MONTHLY.value,
            price_cents=3000,
            duration_days=30,
        )
        db.add(p)
        db.commit()
        return p


@pytest.fixture()
def make_member(session_factory, plan):
    """Insert a member straight into the database with any expiry date."""

    def _make(email="sam@example.com", expires_in_days=30, status=MemberStatus.ACTIVE.value):
        with session_factory() as db:
            member = models.Member(
                full_name="Sam Rao",
                email=email,
                plan_id=plan.id,
                status=status,
                joined_on=date.today() - timedelta(days=60),
                expires_on=date.today() + timedelta(days=expires_in_days),
            )
            db.add(member)
            db.commit()
            return member.id

    return _make

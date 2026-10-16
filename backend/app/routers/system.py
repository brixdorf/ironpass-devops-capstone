from fastapi import APIRouter, Depends, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(tags=["system"])


@router.get("/")
def root():
    return {"service": "ironpass-api", "docs": "/docs"}


@router.get("/health")
def health():
    """Liveness: the process is up. It does not touch the database."""
    return {"status": "ok"}


@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    """Readiness: the API can reach the database."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="database not reachable")
    return {"status": "ready"}


@router.get("/metrics")
def metrics():
    """Prometheus text format."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

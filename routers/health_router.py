# routers/health_router.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from db import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/db-health")
def db_health(db: Session = Depends(get_db)):
    db.execute(func.now())
    return {"db": "ok"}
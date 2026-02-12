# routers/drivers_router.py
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db import get_db
from schemas import DriverCreate, DriverOut, DriverUpdate, PaginatedResponse
from services.drivers_service import (
    create_driver,
    deactivate_driver,
    get_driver,
    list_drivers,
    update_driver,
)

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.post("", response_model=DriverOut, status_code=status.HTTP_201_CREATED)
def create(payload: DriverCreate, db: Session = Depends(get_db)):
    return create_driver(db, payload)


@router.get("", response_model=PaginatedResponse[DriverOut])
def list_(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    is_active: Optional[bool] = None,
    sort: Optional[str] = Query(
        None,
        description="Comma-separated sort fields. Use '-' for DESC. Example: sort=driver_name,-created_at",
        max_length=200,
    ),
):
    return list_drivers(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active,
        sort=sort,
    )


@router.get("/{driver_id}", response_model=DriverOut)
def get_(driver_id: int, db: Session = Depends(get_db)):
    driver = get_driver(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.patch("/{driver_id}", response_model=DriverOut)
def patch(driver_id: int, payload: DriverUpdate, db: Session = Depends(get_db)):
    driver = get_driver(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return update_driver(db, driver, payload)


@router.delete("/{driver_id}", response_model=DriverOut)
def deactivate(driver_id: int, db: Session = Depends(get_db)):
    driver = get_driver(db, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return deactivate_driver(db, driver)
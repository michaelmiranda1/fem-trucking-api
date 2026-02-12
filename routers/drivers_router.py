from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db import get_db
from schemas import DriverCreate, DriverUpdate, DriverOut, DriverListResponse, PaginationMeta
from services.drivers_service import (
    create_driver,
    get_driver,
    update_driver,
    deactivate_driver,
    list_drivers,
)

router = APIRouter(prefix="/drivers", tags=["Drivers"])


@router.post("", response_model=DriverOut, status_code=201)
def create_driver_endpoint(payload: DriverCreate, db: Session = Depends(get_db)):
    return create_driver(db, payload.driver_name)


@router.get("/{driver_id}", response_model=DriverOut)
def get_driver_endpoint(driver_id: int, db: Session = Depends(get_db)):
    return get_driver(db, driver_id)


@router.patch("/{driver_id}", response_model=DriverOut)
def update_driver_endpoint(driver_id: int, payload: DriverUpdate, db: Session = Depends(get_db)):
    return update_driver(db, driver_id, payload.driver_name, payload.is_active)


@router.delete("/{driver_id}", response_model=DriverOut)
def deactivate_driver_endpoint(driver_id: int, db: Session = Depends(get_db)):
    return deactivate_driver(db, driver_id)


@router.get("", response_model=DriverListResponse)
def list_drivers_endpoint(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    sort: Optional[str] = Query(None, description="Comma-separated fields. Use -field for desc. Example: driver_name,-created_at"),
    driver_name_contains: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    items, total, total_pages = list_drivers(
        db=db,
        page=page,
        page_size=page_size,
        sort=sort,
        driver_name_contains=driver_name_contains,
        is_active=is_active,
    )
    return DriverListResponse(
        meta=PaginationMeta(page=page, page_size=page_size, total=total, total_pages=total_pages, sort=sort),
        items=items,
    )
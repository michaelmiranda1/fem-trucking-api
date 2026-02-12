# services/drivers_service.py
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from models import Driver
from schemas import DriverCreate, DriverUpdate
from utils.query import build_order_by, total_pages


def create_driver(db: Session, payload: DriverCreate) -> Driver:
    driver = Driver(driver_name=payload.driver_name)
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


def get_driver(db: Session, driver_id: int) -> Driver | None:
    return db.query(Driver).filter(Driver.driver_id == driver_id).first()


def update_driver(db: Session, driver: Driver, payload: DriverUpdate) -> Driver:
    if payload.driver_name is not None:
        driver.driver_name = payload.driver_name
    if payload.is_active is not None:
        driver.is_active = payload.is_active

    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


def deactivate_driver(db: Session, driver: Driver) -> Driver:
    driver.is_active = False
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


def list_drivers(
    db: Session,
    page: int,
    page_size: int,
    search: Optional[str],
    is_active: Optional[bool],
    sort: Optional[str],
):
    q = db.query(Driver)

    if is_active is not None:
        q = q.filter(Driver.is_active == is_active)

    if search:
        like = f"%{search.strip()}%"
        q = q.filter(Driver.driver_name.ilike(like))

    total = q.count()

    allowed = {
        "driver_id": Driver.driver_id,
        "driver_name": Driver.driver_name,
        "is_active": Driver.is_active,
        "created_at": Driver.created_at,
        "updated_at": Driver.updated_at,
    }
    default_sort = ["-updated_at", "driver_id"]
    order_by = build_order_by(sort=sort, allowed=allowed, default=default_sort, stable_key="driver_id")

    items = (
        q.order_by(*order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages(total, page_size),
    }
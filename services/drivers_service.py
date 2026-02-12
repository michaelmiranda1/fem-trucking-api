from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Driver
from utils.query import apply_pagination, parse_sort, apply_sort


def create_driver(db: Session, driver_name: str) -> Driver:
    driver = Driver(driver_name=driver_name, is_active=True)
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


def get_driver(db: Session, driver_id: int) -> Driver:
    driver = db.get(Driver, driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


def update_driver(db: Session, driver_id: int, driver_name: Optional[str], is_active: Optional[bool]) -> Driver:
    driver = get_driver(db, driver_id)

    if driver_name is not None:
        driver.driver_name = driver_name
    if is_active is not None:
        driver.is_active = is_active

    db.commit()
    db.refresh(driver)
    return driver


def deactivate_driver(db: Session, driver_id: int) -> Driver:
    driver = get_driver(db, driver_id)
    driver.is_active = False
    db.commit()
    db.refresh(driver)
    return driver


def list_drivers(
    db: Session,
    page: int,
    page_size: int,
    sort: Optional[str],
    driver_name_contains: Optional[str],
    is_active: Optional[bool],
) -> Tuple[list[Driver], int, int]:
    q = select(Driver)

    if driver_name_contains:
        q = q.where(Driver.driver_name.ilike(f"%{driver_name_contains}%"))

    if is_active is not None:
        q = q.where(Driver.is_active == is_active)

    allowed = {
        "driver_id": Driver.driver_id,
        "driver_name": Driver.driver_name,
        "is_active": Driver.is_active,
        "created_at": Driver.created_at,
        "updated_at": Driver.updated_at,
    }

    sort_fields = parse_sort(sort, allowed)
    if sort_fields:
        q = apply_sort(q, sort_fields)
    else:
        q = q.order_by(Driver.driver_id.asc())

    paged = apply_pagination(db, q, page, page_size)
    return paged.items, paged.total, paged.total_pages
# services/trucks_service.py
from __future__ import annotations

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from models import Driver, Truck
from schemas import TruckCreate, TruckUpdate
from utils.query import build_order_by, total_pages


def create_truck(db: Session, payload: TruckCreate) -> Truck:
    if payload.driver_id is not None:
        exists = db.query(Driver).filter(Driver.driver_id == payload.driver_id).first()
        if not exists:
            raise ValueError("Driver does not exist")

    truck = Truck(
        unit_number=payload.unit_number,
        vin=payload.vin,
        plate_number=payload.plate_number,
        driver_id=payload.driver_id,
    )
    db.add(truck)
    db.commit()
    db.refresh(truck)
    return truck


def get_truck(db: Session, truck_id: int) -> Truck | None:
    return db.query(Truck).filter(Truck.truck_id == truck_id).first()


def update_truck(db: Session, truck: Truck, payload: TruckUpdate) -> Truck:
    if payload.driver_id is not None:
        exists = db.query(Driver).filter(Driver.driver_id == payload.driver_id).first()
        if not exists:
            raise ValueError("Driver does not exist")
        truck.driver_id = payload.driver_id

    if payload.unit_number is not None:
        truck.unit_number = payload.unit_number
    if payload.vin is not None:
        truck.vin = payload.vin
    if payload.plate_number is not None:
        truck.plate_number = payload.plate_number
    if payload.is_active is not None:
        truck.is_active = payload.is_active

    db.add(truck)
    db.commit()
    db.refresh(truck)
    return truck


def deactivate_truck(db: Session, truck: Truck) -> Truck:
    truck.is_active = False
    db.add(truck)
    db.commit()
    db.refresh(truck)
    return truck


def list_trucks(
    db: Session,
    page: int,
    page_size: int,
    search: Optional[str],
    driver_id: Optional[int],
    is_active: Optional[bool],
    sort: Optional[str],
):
    q = db.query(Truck)

    if is_active is not None:
        q = q.filter(Truck.is_active == is_active)

    if driver_id is not None:
        q = q.filter(Truck.driver_id == driver_id)

    if search:
        like = f"%{search.strip()}%"
        q = q.filter(
            or_(
                Truck.unit_number.ilike(like),
                Truck.vin.ilike(like),
                Truck.plate_number.ilike(like),
            )
        )

    total = q.count()

    allowed = {
        "truck_id": Truck.truck_id,
        "unit_number": Truck.unit_number,
        "vin": Truck.vin,
        "plate_number": Truck.plate_number,
        "driver_id": Truck.driver_id,
        "is_active": Truck.is_active,
        "created_at": Truck.created_at,
        "updated_at": Truck.updated_at,
    }
    default_sort = ["-updated_at", "truck_id"]
    order_by = build_order_by(sort=sort, allowed=allowed, default=default_sort, stable_key="truck_id")

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
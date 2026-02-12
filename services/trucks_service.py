from typing import Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Truck
from utils.query import apply_pagination, parse_sort, apply_sort


def create_truck(
    db: Session,
    unit_number: str,
    plate_number: Optional[str],
    vin: Optional[str],
    is_active: bool,
) -> Truck:
    truck = Truck(
        unit_number=unit_number,
        plate_number=plate_number,
        vin=vin,
        is_active=is_active,
    )
    db.add(truck)
    db.commit()
    db.refresh(truck)
    return truck


def get_truck(db: Session, truck_id: int) -> Truck:
    truck = db.get(Truck, truck_id)
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


def update_truck(
    db: Session,
    truck_id: int,
    unit_number: Optional[str],
    plate_number: Optional[str],
    vin: Optional[str],
    is_active: Optional[bool],
) -> Truck:
    truck = get_truck(db, truck_id)

    if unit_number is not None:
        truck.unit_number = unit_number
    if plate_number is not None:
        truck.plate_number = plate_number
    if vin is not None:
        truck.vin = vin
    if is_active is not None:
        truck.is_active = is_active

    db.commit()
    db.refresh(truck)
    return truck


def deactivate_truck(db: Session, truck_id: int) -> Truck:
    truck = get_truck(db, truck_id)
    truck.is_active = False
    db.commit()
    db.refresh(truck)
    return truck


def list_trucks(
    db: Session,
    page: int,
    page_size: int,
    sort: Optional[str],
    unit_number_contains: Optional[str],
    plate_number_contains: Optional[str],
    vin_contains: Optional[str],
    is_active: Optional[bool],
) -> Tuple[list[Truck], int, int]:
    q = select(Truck)

    if unit_number_contains:
        q = q.where(Truck.unit_number.ilike(f"%{unit_number_contains}%"))
    if plate_number_contains:
        q = q.where(Truck.plate_number.ilike(f"%{plate_number_contains}%"))
    if vin_contains:
        q = q.where(Truck.vin.ilike(f"%{vin_contains}%"))

    if is_active is not None:
        q = q.where(Truck.is_active == is_active)

    allowed = {
        "truck_id": Truck.truck_id,
        "unit_number": Truck.unit_number,
        "plate_number": Truck.plate_number,
        "vin": Truck.vin,
        "is_active": Truck.is_active,
        "created_at": Truck.created_at,
        "updated_at": Truck.updated_at,
    }

    sort_fields = parse_sort(sort, allowed)
    if sort_fields:
        q = apply_sort(q, sort_fields)
    else:
        q = q.order_by(Truck.truck_id.asc())

    paged = apply_pagination(db, q, page, page_size)
    return paged.items, paged.total, paged.total_pages
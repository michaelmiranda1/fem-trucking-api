# main.py
from __future__ import annotations

import math
from typing import Optional, Literal

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from db import get_db
from models import Driver, Truck
from schemas import (
    DriverCreate,
    DriverOut,
    DriverUpdate,
    PaginatedResponse,
    TruckCreate,
    TruckOut,
    TruckUpdate,
)

app = FastAPI(title="FEM Trucking API")


# -------------------------
# Helpers
# -------------------------
def paginate(total: int, page: int, page_size: int) -> int:
    return max(1, math.ceil(total / page_size)) if page_size > 0 else 1


def apply_sorting(model, sort_by: str, sort_dir: str, allowed: dict):
    """
    allowed = {"driver_name": Driver.driver_name, ...}
    """
    if sort_by not in allowed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid sort_by '{sort_by}'. Allowed: {sorted(list(allowed.keys()))}",
        )

    col = allowed[sort_by]
    sort_dir = (sort_dir or "asc").lower()

    if sort_dir == "asc":
        return col.asc()
    if sort_dir == "desc":
        return col.desc()

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Invalid sort_dir. Use 'asc' or 'desc'.",
    )


# -------------------------
# Health
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-health")
def db_health(db: Session = Depends(get_db)):
    db.execute(func.now())
    return {"db": "ok"}


# -------------------------
# Drivers
# -------------------------
@app.post("/drivers", response_model=DriverOut, status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreate, db: Session = Depends(get_db)):
    driver = Driver(driver_name=payload.driver_name)
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@app.get("/drivers", response_model=PaginatedResponse[DriverOut])
def list_drivers(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    is_active: Optional[bool] = None,
    sort_by: str = Query("driver_id"),
    sort_dir: Literal["asc", "desc"] = Query("asc"),
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
    order_clause = apply_sorting(Driver, sort_by, sort_dir, allowed)

    items = (
        q.order_by(order_clause)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    total_pages = paginate(total, page, page_size)
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@app.get("/drivers/{driver_id}", response_model=DriverOut)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@app.patch("/drivers/{driver_id}", response_model=DriverOut)
def update_driver(driver_id: int, payload: DriverUpdate, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    if payload.driver_name is not None:
        driver.driver_name = payload.driver_name
    if payload.is_active is not None:
        driver.is_active = payload.is_active

    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@app.delete("/drivers/{driver_id}", response_model=DriverOut)
def deactivate_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver.is_active = False
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


# -------------------------
# Trucks
# -------------------------
@app.post("/trucks", response_model=TruckOut, status_code=status.HTTP_201_CREATED)
def create_truck(payload: TruckCreate, db: Session = Depends(get_db)):
    if payload.driver_id is not None:
        exists = db.query(Driver).filter(Driver.driver_id == payload.driver_id).first()
        if not exists:
            raise HTTPException(status_code=400, detail="Driver does not exist")

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


@app.get("/trucks", response_model=PaginatedResponse[TruckOut])
def list_trucks(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    driver_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("truck_id"),
    sort_dir: Literal["asc", "desc"] = Query("asc"),
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
    order_clause = apply_sorting(Truck, sort_by, sort_dir, allowed)

    items = (
        q.order_by(order_clause)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    total_pages = paginate(total, page, page_size)
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@app.get("/trucks/{truck_id}", response_model=TruckOut)
def get_truck(truck_id: int, db: Session = Depends(get_db)):
    truck = db.query(Truck).filter(Truck.truck_id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


@app.patch("/trucks/{truck_id}", response_model=TruckOut)
def update_truck(truck_id: int, payload: TruckUpdate, db: Session = Depends(get_db)):
    truck = db.query(Truck).filter(Truck.truck_id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    if payload.driver_id is not None:
        exists = db.query(Driver).filter(Driver.driver_id == payload.driver_id).first()
        if not exists:
            raise HTTPException(status_code=400, detail="Driver does not exist")
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


@app.delete("/trucks/{truck_id}", response_model=TruckOut)
def deactivate_truck(truck_id: int, db: Session = Depends(get_db)):
    truck = db.query(Truck).filter(Truck.truck_id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    truck.is_active = False
    db.add(truck)
    db.commit()
    db.refresh(truck)
    return truck
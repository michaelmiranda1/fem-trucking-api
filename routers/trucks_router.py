# routers/trucks_router.py
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from db import get_db
from schemas import PaginatedResponse, TruckCreate, TruckOut, TruckUpdate
from services.trucks_service import (
    create_truck,
    deactivate_truck,
    get_truck,
    list_trucks,
    update_truck,
)

router = APIRouter(prefix="/trucks", tags=["Trucks"])


@router.post("", response_model=TruckOut, status_code=status.HTTP_201_CREATED)
def create(payload: TruckCreate, db: Session = Depends(get_db)):
    try:
        return create_truck(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=PaginatedResponse[TruckOut])
def list_(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    driver_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    sort: Optional[str] = Query(
        None,
        description="Comma-separated sort fields. Use '-' for DESC. Example: sort=unit_number,-created_at",
        max_length=200,
    ),
):
    return list_trucks(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        driver_id=driver_id,
        is_active=is_active,
        sort=sort,
    )


@router.get("/{truck_id}", response_model=TruckOut)
def get_(truck_id: int, db: Session = Depends(get_db)):
    truck = get_truck(db, truck_id)
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    return truck


@router.patch("/{truck_id}", response_model=TruckOut)
def patch(truck_id: int, payload: TruckUpdate, db: Session = Depends(get_db)):
    truck = get_truck(db, truck_id)
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    try:
        return update_truck(db, truck, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{truck_id}", response_model=TruckOut)
def deactivate(truck_id: int, db: Session = Depends(get_db)):
    truck = get_truck(db, truck_id)
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    return deactivate_truck(db, truck)
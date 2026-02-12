from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db import get_db
from schemas import TruckCreate, TruckUpdate, TruckOut, TruckListResponse, PaginationMeta
from services.trucks_service import (
    create_truck,
    get_truck,
    update_truck,
    deactivate_truck,
    list_trucks,
)

router = APIRouter(prefix="/trucks", tags=["Trucks"])


@router.post("", response_model=TruckOut, status_code=201)
def create_truck_endpoint(payload: TruckCreate, db: Session = Depends(get_db)):
    return create_truck(db, payload.unit_number, payload.plate_number, payload.vin, bool(payload.is_active))


@router.get("/{truck_id}", response_model=TruckOut)
def get_truck_endpoint(truck_id: int, db: Session = Depends(get_db)):
    return get_truck(db, truck_id)


@router.patch("/{truck_id}", response_model=TruckOut)
def update_truck_endpoint(truck_id: int, payload: TruckUpdate, db: Session = Depends(get_db)):
    return update_truck(db, truck_id, payload.unit_number, payload.plate_number, payload.vin, payload.is_active)


@router.delete("/{truck_id}", response_model=TruckOut)
def deactivate_truck_endpoint(truck_id: int, db: Session = Depends(get_db)):
    return deactivate_truck(db, truck_id)


@router.get("", response_model=TruckListResponse)
def list_trucks_endpoint(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    sort: Optional[str] = Query(None, description="Comma-separated fields. Use -field for desc. Example: unit_number,-created_at"),
    unit_number_contains: Optional[str] = Query(None),
    plate_number_contains: Optional[str] = Query(None),
    vin_contains: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    items, total, total_pages = list_trucks(
        db=db,
        page=page,
        page_size=page_size,
        sort=sort,
        unit_number_contains=unit_number_contains,
        plate_number_contains=plate_number_contains,
        vin_contains=vin_contains,
        is_active=is_active,
    )
    return TruckListResponse(
        meta=PaginationMeta(page=page, page_size=page_size, total=total, total_pages=total_pages, sort=sort),
        items=items,
    )
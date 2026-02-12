# schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# -------------------------
# Drivers
# -------------------------
class DriverCreate(BaseModel):
    driver_name: str = Field(..., min_length=1, max_length=255)


class DriverUpdate(BaseModel):
    driver_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None


class DriverOut(BaseModel):
    driver_id: int
    driver_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# -------------------------
# Trucks
# -------------------------
class TruckCreate(BaseModel):
    unit_number: str = Field(..., min_length=1, max_length=50)
    vin: Optional[str] = Field(None, max_length=50)
    plate_number: Optional[str] = Field(None, max_length=50)
    driver_id: Optional[int] = None


class TruckUpdate(BaseModel):
    unit_number: Optional[str] = Field(None, min_length=1, max_length=50)
    vin: Optional[str] = Field(None, max_length=50)
    plate_number: Optional[str] = Field(None, max_length=50)
    driver_id: Optional[int] = None
    is_active: Optional[bool] = None


class TruckOut(BaseModel):
    truck_id: int
    unit_number: str
    vin: Optional[str] = None
    plate_number: Optional[str] = None
    driver_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
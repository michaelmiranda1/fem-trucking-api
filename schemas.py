# schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, ConfigDict
from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# -------------------------
# Drivers
# -------------------------
class DriverBase(BaseModel):
    driver_name: str = Field(..., min_length=1, max_length=100)


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    driver_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class DriverOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_id: int
    driver_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# -------------------------
# Trucks
# -------------------------
class TruckBase(BaseModel):
    unit_number: str = Field(..., min_length=1, max_length=50)
    vin: Optional[str] = Field(None, min_length=1, max_length=64)
    plate_number: Optional[str] = Field(None, min_length=1, max_length=32)
    driver_id: Optional[int] = None


class TruckCreate(TruckBase):
    pass


class TruckUpdate(BaseModel):
    unit_number: Optional[str] = Field(None, min_length=1, max_length=50)
    vin: Optional[str] = Field(None, min_length=1, max_length=64)
    plate_number: Optional[str] = Field(None, min_length=1, max_length=32)
    driver_id: Optional[int] = None
    is_active: Optional[bool] = None


class TruckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    truck_id: int
    unit_number: str
    vin: Optional[str]
    plate_number: Optional[str]
    driver_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
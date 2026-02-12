from datetime import datetime
from typing import Any, Optional, List

from pydantic import BaseModel, Field


# -------------------------
# Shared
# -------------------------
class APIError(BaseModel):
    request_id: str
    error: dict[str, Any]


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    sort: Optional[str] = None


# -------------------------
# Drivers
# -------------------------
class DriverCreate(BaseModel):
    driver_name: str = Field(min_length=1, max_length=255)


class DriverUpdate(BaseModel):
    driver_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    is_active: Optional[bool] = None


class DriverOut(BaseModel):
    driver_id: int
    driver_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DriverListResponse(BaseModel):
    meta: PaginationMeta
    items: List[DriverOut]


# -------------------------
# Trucks
# -------------------------
class TruckCreate(BaseModel):
    unit_number: str = Field(min_length=1, max_length=64)
    plate_number: Optional[str] = Field(default=None, max_length=32)
    vin: Optional[str] = Field(default=None, max_length=32)
    is_active: Optional[bool] = True


class TruckUpdate(BaseModel):
    unit_number: Optional[str] = Field(default=None, min_length=1, max_length=64)
    plate_number: Optional[str] = Field(default=None, max_length=32)
    vin: Optional[str] = Field(default=None, max_length=32)
    is_active: Optional[bool] = None


class TruckOut(BaseModel):
    truck_id: int
    unit_number: str
    plate_number: Optional[str]
    vin: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TruckListResponse(BaseModel):
    meta: PaginationMeta
    items: List[TruckOut]
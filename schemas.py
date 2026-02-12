# schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict, field_validator


# --------------------
# Drivers
# --------------------
class DriverCreate(BaseModel):
    driver_name: str = Field(min_length=1, max_length=120)


class DriverUpdate(BaseModel):
    driver_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    is_active: Optional[bool] = None


class DriverOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    driver_id: int
    driver_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DriverOutWithTrucks(DriverOut):
    trucks: List["TruckOut"] = Field(default_factory=list)


# --------------------
# Trucks
# --------------------
class TruckCreate(BaseModel):
    unit_number: str = Field(min_length=1, max_length=50)
    plate_number: Optional[str] = Field(default=None, max_length=20)
    vin: Optional[str] = Field(default=None, max_length=32)
    driver_id: Optional[int] = None

    @field_validator("plate_number", "vin", mode="before")
    @classmethod
    def empty_string_to_none_create(cls, v):
        # Convert "" or "   " to None so DB NULLs stay clean.
        if v is None:
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class TruckUpdate(BaseModel):
    unit_number: Optional[str] = Field(default=None, min_length=1, max_length=50)
    plate_number: Optional[str] = Field(default=None, max_length=20)
    vin: Optional[str] = Field(default=None, max_length=32)
    is_active: Optional[bool] = None
    driver_id: Optional[int] = None

    @field_validator("plate_number", "vin", mode="before")
    @classmethod
    def empty_string_to_none_update(cls, v):
        # Allows PATCH to clear these fields by sending "" (it becomes None),
        # and also keeps accidental blanks from being stored.
        if v is None:
            return None
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class TruckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    truck_id: int
    unit_number: str
    plate_number: Optional[str]
    vin: Optional[str]
    driver_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Ensures forward refs like "TruckOut" resolve cleanly in all environments
DriverOutWithTrucks.model_rebuild()
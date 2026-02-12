# models.py
from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from db import Base


class Driver(Base):
    __tablename__ = "drivers"

    driver_id = Column(Integer, primary_key=True, index=True)
    driver_name = Column(String(120), nullable=False, index=True)

    is_active = Column(Boolean, nullable=False, server_default="1", default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    trucks = relationship(
        "Truck",
        back_populates="driver",
        lazy="selectin",
    )


class Truck(Base):
    __tablename__ = "trucks"

    truck_id = Column(Integer, primary_key=True, index=True)

    unit_number = Column(String(50), nullable=False, unique=True, index=True)
    plate_number = Column(String(20), nullable=True, index=True)
    vin = Column(String(32), nullable=True, unique=True, index=True)

    is_active = Column(Boolean, nullable=False, server_default="1", default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=True)

    driver = relationship(
        "Driver",
        back_populates="trucks",
        lazy="selectin",
    )
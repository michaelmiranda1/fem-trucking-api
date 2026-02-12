from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class Driver(Base):
    __tablename__ = "drivers"

    driver_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    driver_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Truck(Base):
    __tablename__ = "trucks"

    truck_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    unit_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    plate_number: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    vin: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
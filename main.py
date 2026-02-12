# main.py
from __future__ import annotations

from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from db import engine, get_db
from models import Driver, Truck
from schemas import (
    DriverCreate, DriverUpdate, DriverOut, DriverOutWithTrucks,
    TruckCreate, TruckUpdate, TruckOut
)

app = FastAPI(title="FEM Trucking API", version="0.1.0")


# --------------------
# Health
# --------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-health")
def db_health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"mysql_connected": True}
    except Exception:
        return {"mysql_connected": False}


# --------------------
# Drivers
# --------------------
@app.post("/drivers", response_model=DriverOut, status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreate, db: Session = Depends(get_db)):
    driver = Driver(driver_name=payload.driver_name, is_active=True)
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@app.get("/drivers", response_model=List[DriverOut])
def list_drivers(db: Session = Depends(get_db)):
    return db.query(Driver).order_by(Driver.driver_id.asc()).all()


@app.get("/drivers/{driver_id}", response_model=DriverOutWithTrucks)
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

    data = payload.model_dump(exclude_unset=True)

    if "driver_name" in data:
        driver.driver_name = data["driver_name"]
    if "is_active" in data:
        driver.is_active = data["is_active"]

    db.commit()
    db.refresh(driver)
    return driver


@app.delete("/drivers/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver.is_active = False
    db.commit()
    return None


# --------------------
# Trucks
# --------------------
@app.post("/trucks", response_model=TruckOut, status_code=status.HTTP_201_CREATED)
def create_truck(payload: TruckCreate, db: Session = Depends(get_db)):
    # Validate driver_id if provided
    if payload.driver_id is not None:
        d = db.query(Driver).filter(Driver.driver_id == payload.driver_id).first()
        if not d:
            raise HTTPException(status_code=400, detail="driver_id does not exist")

    # Uniqueness checks
    if db.query(Truck).filter(Truck.unit_number == payload.unit_number).first():
        raise HTTPException(status_code=409, detail="unit_number already exists")
    if payload.vin and db.query(Truck).filter(Truck.vin == payload.vin).first():
        raise HTTPException(status_code=409, detail="vin already exists")

    truck = Truck(
        unit_number=payload.unit_number,
        plate_number=payload.plate_number,
        vin=payload.vin,
        driver_id=payload.driver_id,
        is_active=True,
    )
    db.add(truck)
    db.commit()
    db.refresh(truck)
    return truck


@app.get("/trucks", response_model=List[TruckOut])
def list_trucks(db: Session = Depends(get_db)):
    return db.query(Truck).order_by(Truck.truck_id.asc()).all()


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

    data = payload.model_dump(exclude_unset=True)

    # unit_number (unique)
    if "unit_number" in data and data["unit_number"] != truck.unit_number:
        if db.query(Truck).filter(Truck.unit_number == data["unit_number"]).first():
            raise HTTPException(status_code=409, detail="unit_number already exists")
        truck.unit_number = data["unit_number"]

    # vin (unique, nullable)
    if "vin" in data and data["vin"] != truck.vin:
        new_vin = data["vin"]
        if new_vin and db.query(Truck).filter(Truck.vin == new_vin).first():
            raise HTTPException(status_code=409, detail="vin already exists")
        truck.vin = new_vin

    # plate_number
    if "plate_number" in data:
        truck.plate_number = data["plate_number"]

    # is_active
    if "is_active" in data:
        truck.is_active = data["is_active"]

    # driver_id (supports unassign via null)
    if "driver_id" in data:
        new_driver_id = data["driver_id"]  # can be int or None
        if new_driver_id is not None:
            d = db.query(Driver).filter(Driver.driver_id == new_driver_id).first()
            if not d:
                raise HTTPException(status_code=400, detail="driver_id does not exist")
        truck.driver_id = new_driver_id

    db.commit()
    db.refresh(truck)
    return truck


@app.delete("/trucks/{truck_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_truck(truck_id: int, db: Session = Depends(get_db)):
    truck = db.query(Truck).filter(Truck.truck_id == truck_id).first()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")

    truck.is_active = False
    db.commit()
    return None
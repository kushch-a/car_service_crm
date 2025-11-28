from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import List, Optional
from db import get_db
from schemas.cars import CarCreate, CarUpdate, CarInDB
from crud.cars import (
    get_car_by_id, get_all_cars, create_car, update_car, delete_car, get_car_by_vin
)

router = APIRouter(
    prefix="/cars",
    tags=["Cars"]
)

@router.get("/", response_model=List[CarInDB])
async def read_cars(customer_id: Optional[int] = None, db: AsyncConnection = Depends(get_db)):
    """
    Отримує список всіх машин, або фільтрує їх за customer_id, якщо він вказаний.
    """
    return await get_all_cars(db, customer_id=customer_id)

@router.get("/{car_id}", response_model=CarInDB)
async def read_car(car_id: int, db: AsyncConnection = Depends(get_db)):
    car = await get_car_by_id(db, car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

@router.post("/", response_model=CarInDB, status_code=201)
async def create_new_car(car: CarCreate, db: AsyncConnection = Depends(get_db)):
    return await create_car(db, car)

@router.put("/{car_id}", response_model=CarInDB)
async def update_existing_car(car_id: int, car: CarUpdate, db: AsyncConnection = Depends(get_db)):
    updated = await update_car(db, car_id, car)
    if not updated:
        raise HTTPException(status_code=404, detail="Car not found")
    return updated

@router.delete("/{car_id}", status_code=204)
async def delete_existing_car(car_id: int, db: AsyncConnection = Depends(get_db)):
    success = await delete_car(db, car_id)
    if not success:
        raise HTTPException(status_code=404, detail="Car not found")

@router.get("/by-vin/{vin}", response_model=CarInDB)
async def get_by_vin(vin: str, db: AsyncConnection = Depends(get_db)):
    car = await get_car_by_vin(db, vin)
    if not car:
        raise HTTPException(404, "Car not found")
    return car

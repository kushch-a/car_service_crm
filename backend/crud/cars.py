from typing import List, Optional
from schemas.cars import CarCreate, CarUpdate, CarInDB
from sqlalchemy.ext.asyncio import AsyncConnection

async def get_car_by_id(db: AsyncConnection, car_id: int) -> Optional[CarInDB]:
    query = "SELECT * FROM cars WHERE id = :id"
    row = await db.fetch_one(query, {"id": car_id})
    return CarInDB(**dict(row)) if row else None

async def get_all_cars(db: AsyncConnection) -> List[CarInDB]:
    query = "SELECT * FROM cars ORDER BY id"
    rows = await db.fetch_all(query)
    return [CarInDB(**dict(row)) for row in rows]

async def create_car(db: AsyncConnection, car: CarCreate) -> CarInDB:
    query = "INSERT INTO cars (customer_id, brand, model, year, vin) VALUES (:customer_id, :brand, :model, :year, :vin) RETURNING *"
    row = await db.fetch_one(query, car.dict())
    return CarInDB(**dict(row))

async def update_car(db: AsyncConnection, car_id: int, car: CarUpdate) -> Optional[CarInDB]:
    query = "UPDATE cars SET customer_id = :customer_id, brand = :brand, model = :model, year = :year, vin = :vin, updated_at = CURRENT_TIMESTAMP WHERE id = :id RETURNING *"
    row = await db.fetch_one(query, {**car.dict(), "id": car_id})
    return CarInDB(**dict(row)) if row else None

async def delete_car(db: AsyncConnection, car_id: int) -> bool:
    query = "DELETE FROM cars WHERE id = :id"
    await db.execute(query, {"id": car_id})
    return True

async def get_car_by_vin(db: AsyncConnection, vin: str):
    query = "SELECT * FROM cars WHERE vin = :vin"
    row = await db.fetch_one(query, {"vin": vin})
    if row:
        return CarInDB(**dict(row))
    return None

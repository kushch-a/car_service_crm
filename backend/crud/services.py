from typing import List, Optional
from schemas.services import ServiceCreate, ServiceUpdate, ServiceInDB
from sqlalchemy.ext.asyncio import AsyncConnection


async def get_all_services(db: AsyncConnection) -> List[ServiceInDB]:
    query = "SELECT * FROM services ORDER BY id;"
    rows = await db.fetch_all(query)
    return [ServiceInDB(**dict(row)) for row in rows]


async def get_service_by_id(db: AsyncConnection, service_id: int) -> Optional[ServiceInDB]:
    query = "SELECT * FROM services WHERE id = :id;"
    row = await db.fetch_one(query, {"id": service_id})
    if row:
        return ServiceInDB(**dict(row))
    return None


async def create_service(db: AsyncConnection, service: ServiceCreate) -> ServiceInDB:
    query = """
        INSERT INTO services (name, description, price, duration)
        VALUES (:name, :description, :price, :duration)
        RETURNING *;
    """
    row = await db.fetch_one(query, service.dict())
    return ServiceInDB(**dict(row))


async def update_service(db: AsyncConnection, service_id: int, service: ServiceUpdate) -> Optional[ServiceInDB]:
    query = "UPDATE services SET name = :name, description = :description, price = :price, duration = :duration, updated_at = CURRENT_TIMESTAMP WHERE id = :id RETURNING *;"
    values = service.dict()
    values["id"] = service_id
    row = await db.fetch_one(query, values)
    if row:
        return ServiceInDB(**dict(row))
    return None


async def delete_service(db: AsyncConnection, service_id: int) -> bool:
    query = "DELETE FROM services WHERE id = :id;"
    result = await db.execute(query, {"id": service_id})
    return result.rowcount > 0


async def delete_service_from_db(db: AsyncConnection, service_id: int):
    query = "DELETE FROM services WHERE id = :id"
    await db.execute(query, {"id": service_id})

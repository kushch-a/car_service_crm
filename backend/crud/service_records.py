from typing import List, Optional
from schemas.service_records import ServiceRecordCreate, ServiceRecordUpdate
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

async def get_all_service_records(db: AsyncConnection):
    query = text("SELECT * FROM service_records ORDER BY date DESC")
    result = await db.execute(query)
    return result.mappings().all()

async def get_service_record_by_id(db: AsyncConnection, record_id: int):
    query = text("SELECT * FROM service_records WHERE id = :id")
    result = await db.execute(query, {"id": record_id})
    return result.mappings().first()

async def create_service_record(db: AsyncConnection, record: ServiceRecordCreate):
    query = text("""
        INSERT INTO service_records (car_id, service_id, performed_by, date, mileage, notes, invoice_id)
        VALUES (:car_id, :service_id, :performed_by, :date, :mileage, :notes, :invoice_id)
        RETURNING *
    """)
    result = await db.execute(query, record.dict())
    return result.mappings().first()

async def update_service_record(db: AsyncConnection, record_id: int, record: ServiceRecordUpdate):
    query = text("""
        UPDATE service_records
        SET car_id = :car_id,
            service_id = :service_id,
            performed_by = :performed_by,
            date = :date,
            mileage = :mileage,
            notes = :notes,
            invoice_id = :invoice_id,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :id
        RETURNING *
    """)
    values = record.dict()
    values["id"] = record_id
    result = await db.execute(query, values)
    return result.mappings().first()

async def delete_service_record(db: AsyncConnection, record_id: int):
    query = text("DELETE FROM service_records WHERE id = :id")
    result = await db.execute(query, {"id": record_id})
    return result.rowcount > 0

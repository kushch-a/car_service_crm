from fastapi import APIRouter, Depends, HTTPException
from typing import List
from schemas.service_records import ServiceRecordCreate, ServiceRecordUpdate, ServiceRecordInDB
from crud.service_records import (
    get_all_service_records,
    get_service_record_by_id,
    create_service_record,
    update_service_record,
    delete_service_record,
)
from db import get_db
from sqlalchemy.ext.asyncio import AsyncConnection
from crud.invoices import create_invoice
from crud.invoice_items import create_invoice_item
from crud.cars import get_car_by_id
from crud.services import get_service_by_id
from datetime import datetime
from decimal import Decimal

router = APIRouter( 
    prefix="/service-records",
    tags=["Service Records"]
)

@router.get("/", response_model=List[ServiceRecordInDB])
async def read_records(db: AsyncConnection = Depends(get_db)):
    return await get_all_service_records(db)

@router.get("/{record_id}", response_model=ServiceRecordInDB)
async def read_record(record_id: int, db: AsyncConnection = Depends(get_db)):
    record = await get_service_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Service record not found")
    return record

@router.post("/", response_model=ServiceRecordInDB, status_code=201)
async def create_record(record: ServiceRecordCreate, db: AsyncConnection = Depends(get_db)):
    return await create_service_record(db, record)

@router.put("/{record_id}", response_model=ServiceRecordInDB)
async def update_record(record_id: int, record: ServiceRecordUpdate, db: AsyncConnection = Depends(get_db)):
    updated = await update_service_record(db, record_id, record)
    if not updated:
        raise HTTPException(status_code=404, detail="Service record not found")
    return updated

@router.delete("/{record_id}", status_code=204)
async def delete_record(record_id: int, db: AsyncConnection = Depends(get_db)):
    success = await delete_service_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Service record not found")

@router.post("/{record_id}/create-invoice", response_model=None, status_code=201)
async def create_invoice_for_record(record_id: int, db: AsyncConnection = Depends(get_db)):
    # 1. Отримати service_record
    record = await get_service_record_by_id(db, record_id)
    if not record:
        raise HTTPException(404, "Service record not found")
    if record.invoice_id:
        raise HTTPException(400, "Invoice already exists for this record")

    # 2. Отримати car, service
    car = await get_car_by_id(db, record.car_id)
    service = await get_service_by_id(db, record.service_id)
    if not car or not service:
        raise HTTPException(400, "Car or service not found")

    # 3. Створити invoice
    invoice_data = {
        "customer_id": car.customer_id,
        "status": "unpaid",
        "issued_at": datetime.utcnow(),
        "due_date": datetime.utcnow(),
        "total": Decimal(service.price)
    }
    invoice = await create_invoice(db, invoice_data)

    # 4. Створити invoice_item
    item_data = {
        "invoice_id": invoice.id,
        "service_id": service.id,
        "quantity": 1,
        "unit_price": Decimal(service.price),
        "total": Decimal(service.price)
    }
    await create_invoice_item(db, item_data)

    # 5. Оновити service_record (invoice_id)
    await update_service_record(db, record_id, {"invoice_id": invoice.id})

    return {"invoice_id": invoice.id}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import List, Any
from schemas.invoices import InvoiceCreate, InvoiceUpdate, InvoiceInDB
from schemas.users import User
from crud.invoices import (
    create_invoice, get_invoice_by_id, get_all_invoices,
    update_invoice as crud_update_invoice, delete_invoice
)
from db import get_db
from crud.invoice_items import create_invoice_item
from schemas.invoice_items import InvoiceItemCreate
from crud.users import get_current_user
from sqlalchemy import text

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"]
)

@router.post("/", response_model=InvoiceInDB, status_code=201)
async def create(
    invoice: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncConnection = Depends(get_db)
) -> Any:
    if current_user.role == "master":
        raise HTTPException(403, "Masters cannot create invoices")
    return await create_invoice(db, invoice)

@router.get("/", response_model=List[InvoiceInDB])
async def get_invoices(
    current_user: User = Depends(get_current_user),
    db: AsyncConnection = Depends(get_db)
):
    if current_user.role == "master":
        # Показати лише свої інвойси
        query = """
            SELECT * FROM invoices WHERE worker_id = :worker_id
        """
        rows = await db.fetch_all(query, {"worker_id": current_user.id})
        return [InvoiceInDB(**dict(row)) for row in rows]
    else:
        # Адмін/менеджер бачить всі
        return await get_all_invoices(db)

@router.get("/{invoice_id}", response_model=InvoiceInDB)
async def read(invoice_id: int, db: AsyncConnection = Depends(get_db)):
    query = text("SELECT * FROM invoices WHERE id = :id")
    result = await db.fetch_one(query, {"id": invoice_id})
    if not result:
        raise HTTPException(404, "Invoice not found")
    return InvoiceInDB(**dict(result))

@router.patch("/{invoice_id}", response_model=InvoiceInDB)
async def update_invoice(
    invoice_id: int,
    update_data: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncConnection = Depends(get_db)
) -> Any:
    invoice = await get_invoice_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
        
    if current_user.role == "master":
        if invoice.worker_id != current_user.id:
            raise HTTPException(403, "Not authorized")
        # Masters can only update work_status and payment_status
        allowed_fields = {"work_status", "payment_status"}
        filtered_data = {k: v for k, v in update_data.dict().items() if k in allowed_fields}
        update_data = InvoiceUpdate(**filtered_data)
    
    return await crud_update_invoice(db, invoice_id, update_data)

@router.delete("/{invoice_id}", status_code=204)
async def delete(invoice_id: int, db: AsyncConnection = Depends(get_db)):
    await delete_invoice(db, invoice_id)

@router.post("/invoices", response_model=InvoiceInDB)
async def create_invoice_with_item(invoice: InvoiceCreate, db=Depends(get_db)) -> Any:
    # 1. Створюємо інвойс (без service_id)
    invoice_data = invoice.dict().copy()
    service_id = invoice_data.pop("service_id")  # Витягуємо service_id
    new_invoice = await create_invoice(db, InvoiceCreate(**invoice_data))

    # 2. Додаємо перший invoice_item
    item = InvoiceItemCreate(
        invoice_id=new_invoice.id,
        service_id=service_id,
        quantity=1,
        unit_price=invoice.total,  # або діставай ціну з сервісу
        total=invoice.total
    )
    await create_invoice_item(db, item)

    return new_invoice 
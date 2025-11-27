from schemas.invoices import InvoiceCreate, InvoiceUpdate, InvoiceInDB
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import List, Optional
from sqlalchemy.future import select


async def create_invoice(db, invoice: InvoiceCreate) -> InvoiceInDB:
    query = """
        INSERT INTO invoices (customer_id, car_id, worker_id, service_id, total_amount, payment_status, work_status)
        VALUES (:customer_id, :car_id, :worker_id, :service_id, :total_amount, :payment_status, :work_status)
        RETURNING id, customer_id, car_id, worker_id, service_id, total_amount, payment_status, work_status, 
                created_at, updated_at, issue_date, due_date, created_by
    """
    params = {
        "customer_id": invoice.customer_id,
        "car_id": invoice.car_id,
        "worker_id": invoice.worker_id,
        "service_id": invoice.service_id,
        "total_amount": invoice.total_amount,
        "payment_status": invoice.payment_status,
        "work_status": invoice.work_status,
    }
    row = await db.fetch_one(query, params)
    return InvoiceInDB(**dict(row))

async def get_invoice_by_id(db, invoice_id):
    query = "SELECT * FROM invoices WHERE id = :id"
    row = await db.fetch_one(query, {"id": invoice_id})
    if row:
        return InvoiceInDB(**dict(row))
    return None

async def get_all_invoices(db):
    query = text("SELECT * FROM invoices")
    result = await db.fetch_all(query)
    rows = result
    return [InvoiceInDB(**dict(row)) for row in rows]

async def update_invoice(db: AsyncConnection, invoice_id: int, invoice: InvoiceUpdate) -> Optional[InvoiceInDB]:
    fields = {k: v for k, v in invoice.dict(exclude_unset=True).items()}
    set_clause = ", ".join([f"{k} = :{k}" for k in fields])
    if not set_clause:
        return await get_invoice_by_id(db, invoice_id)
    query = f"""
        UPDATE invoices SET {set_clause}, updated_at = now()
        WHERE id = :id RETURNING *
    """
    fields["id"] = invoice_id
    row = await db.fetch_one(query, fields)
    if row:
        return InvoiceInDB(**dict(row))
    return None

async def delete_invoice(db: AsyncConnection, invoice_id: int) -> bool:
    query = "DELETE FROM invoices WHERE id = :id"
    await db.execute(query, {"id": invoice_id})
    return True 
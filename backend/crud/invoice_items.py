from schemas.invoice_items import InvoiceItemCreate, InvoiceItemUpdate, InvoiceItemInDB
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import List, Optional

async def create_invoice_item(db: AsyncConnection, item: InvoiceItemCreate) -> InvoiceItemInDB:
    query = text("""
        INSERT INTO invoice_items (invoice_id, service_id, quantity, unit_price, total)
        VALUES (:invoice_id, :service_id, :quantity, :unit_price, :total)
        RETURNING *
    """)
    result = await db.execute(query, item.dict())
    row = result.fetchone()
    return InvoiceItemInDB(**dict(row))

async def get_invoice_item_by_id(db: AsyncConnection, item_id: int) -> Optional[InvoiceItemInDB]:
    query = text("SELECT * FROM invoice_items WHERE id = :id")
    result = await db.execute(query, {"id": item_id})
    row = result.fetchone()
    if row:
        return InvoiceItemInDB(**dict(row))
    return None

async def get_items_by_invoice(db: AsyncConnection, invoice_id: int) -> List[InvoiceItemInDB]:
    query = text("SELECT * FROM invoice_items WHERE invoice_id = :invoice_id")
    result = await db.execute(query, {"invoice_id": invoice_id})
    rows = result.fetchall()
    return [InvoiceItemInDB(**dict(row)) for row in rows]

async def update_invoice_item(db: AsyncConnection, item_id: int, item: InvoiceItemUpdate) -> Optional[InvoiceItemInDB]:
    fields = {k: v for k, v in item.dict(exclude_unset=True).items()}
    set_clause = ", ".join([f"{k} = :{k}" for k in fields])
    if not set_clause:
        return await get_invoice_item_by_id(db, item_id)
    query = text(f"""
        UPDATE invoice_items SET {set_clause}, updated_at = now()
        WHERE id = :id RETURNING *
    """)
    fields["id"] = item_id
    result = await db.execute(query, fields)
    row = result.fetchone()
    if row:
        return InvoiceItemInDB(**dict(row))
    return None

async def delete_invoice_item(db: AsyncConnection, item_id: int) -> bool:
    query = text("DELETE FROM invoice_items WHERE id = :id")
    await db.execute(query, {"id": item_id})
    return True 
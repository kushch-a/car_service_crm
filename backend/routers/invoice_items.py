from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import List
from schemas.invoice_items import InvoiceItemCreate, InvoiceItemUpdate, InvoiceItemInDB
from crud.invoice_items import (
    create_invoice_item, get_invoice_item_by_id, get_items_by_invoice,
    update_invoice_item, delete_invoice_item
)
from db import get_db

router = APIRouter(
    prefix="/invoice-items",
    tags=["Invoice Items"]
)

@router.post("/", response_model=InvoiceItemInDB, status_code=201)
async def create(item: InvoiceItemCreate, db: AsyncConnection = Depends(get_db)):
    return await create_invoice_item(db, item)

@router.get("/by-invoice/{invoice_id}", response_model=List[InvoiceItemInDB])
async def by_invoice(invoice_id: int, db: AsyncConnection = Depends(get_db)):
    return await get_items_by_invoice(db, invoice_id)

@router.get("/{item_id}", response_model=InvoiceItemInDB)
async def read(item_id: int, db: AsyncConnection = Depends(get_db)):
    item = await get_invoice_item_by_id(db, item_id)
    if not item:
        raise HTTPException(404, "Invoice item not found")
    return item

@router.patch("/{item_id}", response_model=InvoiceItemInDB)
async def update(item_id: int, item: InvoiceItemUpdate, db: AsyncConnection = Depends(get_db)):
    updated = await update_invoice_item(db, item_id, item)
    if not updated:
        raise HTTPException(404, "Invoice item not found")
    return updated

@router.delete("/{item_id}", status_code=204)
async def delete(item_id: int, db: AsyncConnection = Depends(get_db)):
    await delete_invoice_item(db, item_id) 
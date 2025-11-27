from fastapi import APIRouter, HTTPException, Depends
from typing import List
from schemas.customers import CustomerCreate, CustomerUpdate, CustomerInDB
from crud.customers import (
    get_customer_by_id,
    get_all_customers,
    create_customer,
    update_customer_in_db,
    delete_customer_in_db,
)
from db import get_db
from sqlalchemy.ext.asyncio import AsyncConnection
from schemas.users import User
from auth.deps import get_current_user

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)

@router.get("/", response_model=List[CustomerInDB])
async def read_customers(db: AsyncConnection = Depends(get_db)):
    return await get_all_customers(db)

@router.get("/{customer_id}", response_model=CustomerInDB)
async def read_customer(customer_id: int, db: AsyncConnection = Depends(get_db)):
    customer = await get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/", response_model=CustomerInDB, status_code=201)
async def create_new_customer(customer: CustomerCreate, db: AsyncConnection = Depends(get_db)):
    return await create_customer(db, customer)

@router.put("/{customer_id}", response_model=CustomerInDB)
async def update_existing_customer(customer_id: int, customer: CustomerUpdate, db: AsyncConnection = Depends(get_db)):
    updated = await update_customer_in_db(db, customer_id, customer)
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated

@router.patch("/{customer_id}", response_model=CustomerInDB)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncConnection = Depends(get_db)
):
    if current_user["role"] not in ("admin", "manager"):
        raise HTTPException(403, "Тільки адмін або менеджер може редагувати клієнтів")
    customer = await get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(404, "Клієнта не знайдено")
    return await update_customer_in_db(db, customer_id, customer_update)

@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncConnection = Depends(get_db)
):
    if current_user["role"] not in ("admin", "manager"):
        raise HTTPException(403, "Тільки адмін або менеджер може видаляти клієнтів")
    await delete_customer_in_db(db, customer_id)
    return

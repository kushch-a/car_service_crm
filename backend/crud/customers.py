from schemas.customers import CustomerCreate, CustomerUpdate, CustomerInDB
from sqlalchemy.ext.asyncio import AsyncConnection
from typing import List, Optional

async def get_all_customers(db: AsyncConnection) -> List[CustomerInDB]:
    query = """
        SELECT id, first_name, last_name, phone, email, address, created_at, updated_at
        FROM customers
        ORDER BY id;
    """
    rows = await db.fetch_all(query)
    return [CustomerInDB(**dict(row)) for row in rows]

async def get_customer_by_id(db: AsyncConnection, customer_id: int) -> Optional[CustomerInDB]:
    query = """
        SELECT id, first_name, last_name, phone, email, address, created_at, updated_at
        FROM customers
        WHERE id = :id;
    """
    row = await db.fetch_one(query, {"id": customer_id})
    if row:
        return CustomerInDB(**dict(row))
    return None

async def create_customer(db: AsyncConnection, customer: CustomerCreate) -> CustomerInDB:
    query = """
        INSERT INTO customers (first_name, last_name, phone, email, address)
        VALUES (:first_name, :last_name, :phone, :email, :address)
        RETURNING id, first_name, last_name, phone, email, address, created_at, updated_at;
    """
    row = await db.fetch_one(query, customer.dict())
    return CustomerInDB(**dict(row))

async def update_customer_in_db(db: AsyncConnection, customer_id: int, customer_update: CustomerUpdate):
    query = """
        UPDATE customers
        SET first_name = :first_name,
            last_name = :last_name,
            phone = :phone,
            email = :email,
            address = :address
        WHERE id = :id
        RETURNING id, first_name, last_name, phone, email, address, created_at, updated_at
    """
    params = {
        "id": customer_id,
        "first_name": customer_update.first_name,
        "last_name": customer_update.last_name,
        "phone": customer_update.phone,
        "email": customer_update.email,
        "address": customer_update.address,
    }
    row = await db.fetch_one(query, params)
    if row:
        return CustomerInDB(**dict(row))
    return None

async def delete_customer_in_db(db: AsyncConnection, customer_id: int) -> bool:
    result = await db.execute(
        """
        DELETE FROM customers
        WHERE id = :id
        RETURNING id;
        """,
        {"id": customer_id}
    )
    row = result.fetchone()
    return row is not None


from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class InvoiceBase(BaseModel):
    customer_id: int
    car_id: int
    worker_id: int
    service_id: int
    total_amount: float
    payment_status: str = "unpaid"
    work_status: str = "new"

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    customer_id: Optional[int] = None
    car_id: Optional[int] = None
    worker_id: Optional[int] = None
    service_id: Optional[int] = None
    total_amount: Optional[float] = None
    payment_status: Optional[str] = None
    work_status: Optional[str] = None

class InvoiceInDB(InvoiceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    issue_date: datetime
    due_date: Optional[datetime]
    created_by: Optional[int]

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class InvoiceItemBase(BaseModel):
    invoice_id: int
    service_id: int
    quantity: int
    unit_price: Decimal
    total: Decimal

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItemUpdate(BaseModel):
    quantity: Optional[int]
    unit_price: Optional[Decimal]
    total: Optional[Decimal]

class InvoiceItemInDB(InvoiceItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

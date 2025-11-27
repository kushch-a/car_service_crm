# schemas/invoices.py
from pydantic import BaseModel

class InvoiceRead(BaseModel):
    id: int
    customer_id: int
    car_id: int
    total: float
    status: str

class InvoiceCreate(BaseModel):
    customer_id: int
    car_id: int
    total: float
    status: str
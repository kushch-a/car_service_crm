from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ServiceRecordBase(BaseModel):
    car_id: int
    service_id: int
    performed_by: int
    date: datetime
    mileage: Optional[int] = None
    notes: Optional[str] = None
    invoice_id: Optional[int] = None

class ServiceRecordCreate(ServiceRecordBase):
    pass

class ServiceRecordUpdate(ServiceRecordBase):
    pass

class ServiceRecordInDB(ServiceRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

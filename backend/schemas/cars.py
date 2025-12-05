from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class CarBase(BaseModel):
    customer_id: int
    brand: str
    model: str
    year: int
    vin: Optional[str] = None

class CarCreate(CarBase):
    pass

class CarUpdate(CarBase):
    pass

class CarInDB(CarBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

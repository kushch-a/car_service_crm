from pydantic import ConfigDict, BaseModel
from typing import Optional
from datetime import datetime


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float  # у форматі 9999.99
    duration: int  # тривалість у хвилинах


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(ServiceBase):
    pass


class ServiceInDB(ServiceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from enum import Enum

# --- Value Objects & Enums ---

class InvoiceStatus(Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PAID = "paid"
    CANCELLED = "cancelled"

# --- CRM Context ---

@dataclass
class Car:
    vin: str
    make: str
    model: str
    year: int
    owner_id: int

    def update_mileage(self, new_mileage: int):
        # Тут може бути логіка валідації (пробіг не може бути меншим за попередній)
        pass

@dataclass
class Customer:
    id: int
    first_name: str
    last_name: str
    phone: str
    cars: List[Car] = field(default_factory=list)

    def add_car(self, car: Car):
        self.cars.append(car)

# --- Service Operations Context ---

@dataclass
class ServiceItem:
    id: int
    name: str
    price: float
    duration_minutes: int

@dataclass
class ServiceRecord:
    id: int
    car_vin: str
    service_id: int
    mechanic_id: int
    date: datetime
    status: str = "scheduled"

    def complete_work(self):
        self.status = "completed"
        # Логіка оновлення історії авто

# --- Billing Context ---

@dataclass
class InvoiceLine:
    service_name: str
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price

@dataclass
class Invoice:
    id: int
    customer_id: int
    items: List[InvoiceLine] = field(default_factory=list)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)

    def add_item(self, item: InvoiceLine):
        if self.status != InvoiceStatus.DRAFT:
            raise Exception("Cannot add items to issued invoice")
        self.items.append(item)

    def calculate_total(self) -> float:
        return sum(item.total for item in self.items)

    def issue(self):
        # Логіка фіналізації рахунку
        self.status = InvoiceStatus.ISSUED
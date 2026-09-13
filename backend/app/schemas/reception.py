from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.common import ORMModel


class ReceptionRead(ORMModel):
    id: int
    supplier_id: int
    branch_id: int
    employee_id: int
    received_at: datetime | None
    purchase_order_ref: str | None


class ReceptionItem(BaseModel):
    variant_id: int
    quantity: int
    cost_price: Decimal


class ReceptionCreate(BaseModel):
    supplier_id: int
    branch_id: int
    employee_id: int | None = None
    purchase_order_ref: str | None = None
    items: list[ReceptionItem] = []
    notes: str | None = None


class ReceptionDetailRead(ORMModel):
    id: int
    variant_id: int
    quantity: int
    cost_price: Decimal


class ReceptionFullRead(ReceptionRead):
    details: list[ReceptionDetailRead] = []

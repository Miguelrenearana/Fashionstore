from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.schemas.common import ORMModel


class HistorySaleItem(BaseModel):
    variant_id: int
    garment_name: str
    size_name: str
    color_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class HistorySaleRead(ORMModel):
    id: int
    invoice_number: str
    branch_name: str | None = None
    total_amount: Decimal
    status: str
    paid_at: datetime | None = None
    items: list[HistorySaleItem] = []
    receipt_url: str | None = None
    receipt_type: str | None = None


class HistoryReservationItem(BaseModel):
    variant_id: int
    garment_name: str
    size_name: str
    color_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class HistoryReservationRead(ORMModel):
    id: int
    pickup_code: str
    branch_name: str | None = None
    total_amount: Decimal
    status: str
    created_at: datetime
    expires_at: datetime | None = None
    items: list[HistoryReservationItem] = []


class PurchaseHistoryItem(BaseModel):
    type: Literal["sale", "reservation"]
    id: int
    reference: str
    date: datetime
    total_amount: Decimal
    status: str
    branch_name: str | None = None
    items_count: int


class PurchaseHistoryResponse(BaseModel):
    items: list[PurchaseHistoryItem]
    total: int
    page: int
    size: int
    pages: int

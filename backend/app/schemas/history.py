from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Literal

from pydantic import BaseModel, Field

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
    branch_name: Optional[str] = None
    total_amount: Decimal
    status: str
    paid_at: Optional[datetime] = None
    items: List[HistorySaleItem] = []
    receipt_url: Optional[str] = None
    receipt_type: Optional[str] = None


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
    branch_name: Optional[str] = None
    total_amount: Decimal
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    items: List[HistoryReservationItem] = []


class PurchaseHistoryItem(BaseModel):
    type: Literal["sale", "reservation"]
    id: int
    reference: str
    date: datetime
    total_amount: Decimal
    status: str
    branch_name: Optional[str] = None
    items_count: int


class PurchaseHistoryResponse(BaseModel):
    items: List[PurchaseHistoryItem]
    total: int
    page: int
    size: int
    pages: int
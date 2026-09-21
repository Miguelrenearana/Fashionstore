from datetime import datetime
from typing import Optional

from app.schemas.common import ORMModel


class ReceiptDetailRead(ORMModel):
    id: int
    variant_id: int
    quantity: int
    unit_price: float
    line_total: float


class ReceiptRead(ORMModel):
    id: int
    sale_id: int
    type: str
    rnc_or_cuf: Optional[str] = None
    document_url: Optional[str] = None
    created_at: datetime


class ReceiptDetailRead(ORMModel):
    id: int
    sale_id: int
    type: str
    rnc_or_cuf: Optional[str] = None
    document_url: Optional[str] = None
    created_at: datetime
    total_amount: float
    status: str
    branch_name: Optional[str] = None
    items: list["ReceiptDetailRead"] = []


class ReceiptListItem(ORMModel):
    id: int
    sale_id: int
    type: str
    rnc_or_cuf: Optional[str] = None
    total_amount: float
    status: str
    created_at: datetime
    branch_name: Optional[str] = None


class ReceiptPageResponse(ORMModel):
    items: list[ReceiptListItem]
    total: int
    page: int
    size: int
    pages: int

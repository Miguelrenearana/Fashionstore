from datetime import datetime

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
    rnc_or_cuf: str | None = None
    document_url: str | None = None
    created_at: datetime


class ReceiptDetailRead(ORMModel):
    id: int
    sale_id: int
    type: str
    rnc_or_cuf: str | None = None
    document_url: str | None = None
    created_at: datetime
    total_amount: float
    status: str
    branch_name: str | None = None
    items: list["ReceiptDetailRead"] = []


class ReceiptListItem(ORMModel):
    id: int
    sale_id: int
    type: str
    rnc_or_cuf: str | None = None
    total_amount: float
    status: str
    created_at: datetime
    branch_name: str | None = None


class ReceiptPageResponse(ORMModel):
    items: list[ReceiptListItem]
    total: int
    page: int
    size: int
    pages: int

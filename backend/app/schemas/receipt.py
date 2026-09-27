from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ReceiptItemRead(ORMModel):
    """Línea de detalle del comprobante (calculada desde `venta_detalle`)."""

    variant_id: int
    garment_name: str | None = None
    size_name: str | None = None
    color_name: str | None = None
    quantity: int
    unit_price: float
    line_total: float


class ReceiptRead(ORMModel):
    """CU-24: comprobante emitido para una venta."""

    id: int
    sale_id: int
    type: str
    rnc_or_cuf: str | None = None
    document_url: str | None = None
    created_at: datetime
    invoice_number: str | None = None
    total_amount: float = 0
    status: str = "UNKNOWN"
    branch_name: str | None = None
    items: list[ReceiptItemRead] = []


class ReceiptListItem(ORMModel):
    id: int
    sale_id: int
    type: str
    rnc_or_cuf: str | None = None
    total_amount: float
    status: str
    created_at: datetime
    branch_name: str | None = None


class ReceiptPageResponse(BaseModel):
    items: list[ReceiptListItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    size: int = 20
    pages: int = 0

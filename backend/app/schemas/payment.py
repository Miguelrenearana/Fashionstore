from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PaymentCreate(BaseModel):
    sale_id: int
    amount: float = 0
    method: str = "card"
    gateway: str = "mock"


class PaymentRead(ORMModel):
    id: int
    sale_id: int | None
    amount: float
    currency: str
    method: str
    status: str
    gateway_reference: str | None = None


class PaymentConfirm(BaseModel):
    token: str | None = None
    gateway_reference: str | None = None


# CU-25: Payment initiation/confirmation schemas
class PaymentInitRequest(BaseModel):
    sale_id: int = Field(gt=0)
    method: str = Field(default="static_qr", pattern="^(mock|static_qr|pagosnet|ebanx|card|cash)$")
    gateway: Optional[str] = None


class PaymentInitResponse(BaseModel):
    reference: str
    status: str
    payment_url: Optional[str] = None
    qr_svg_url: Optional[str] = None
    payment_page_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    raw: dict = {}


class PaymentConfirmRequest(BaseModel):
    gateway_reference: str


class PaymentStatusResponse(BaseModel):
    reference: str
    status: str
    amount: float
    currency: str
    verified_at: Optional[datetime] = None
    verification_method: Optional[str] = None


class PaymentRefundRequest(BaseModel):
    gateway_reference: str
    amount: Optional[float] = None
    reason: Optional[str] = None

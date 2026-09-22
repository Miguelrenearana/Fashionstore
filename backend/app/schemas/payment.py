from datetime import datetime

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
    gateway: str | None = None


class PaymentInitResponse(BaseModel):
    reference: str
    status: str
    payment_url: str | None = None
    qr_svg_url: str | None = None
    payment_page_url: str | None = None
    expires_at: datetime | None = None
    raw: dict = {}


class PaymentConfirmRequest(BaseModel):
    gateway_reference: str


class PaymentStatusResponse(BaseModel):
    reference: str
    status: str
    amount: float
    currency: str
    verified_at: datetime | None = None
    verification_method: str | None = None


class PaymentRefundRequest(BaseModel):
    gateway_reference: str
    amount: float | None = None
    reason: str | None = None

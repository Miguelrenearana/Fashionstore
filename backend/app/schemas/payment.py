from pydantic import BaseModel

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

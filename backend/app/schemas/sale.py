from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class SaleDetailRead(ORMModel):
    id: int
    variant_id: int
    quantity: int
    unit_price: float


class SaleRead(ORMModel):
    id: int
    invoice_number: str
    branch_id: int
    total_amount: float
    payment_method: str
    status: str | None = None
    details: list[SaleDetailRead] = []


class SaleGenerate(BaseModel):
    branch_id: int
    items: list[dict] = Field(min_length=1)  # [{variant_id, quantity}]
    payment_method: str = "card"

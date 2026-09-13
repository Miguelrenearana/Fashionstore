from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel


class SaleItem(BaseModel):
    variant_id: int
    quantity: int = Field(gt=0)


class SaleDetailRead(ORMModel):
    id: int
    variant_id: int
    quantity: int
    unit_price: float


class SaleRead(ORMModel):
    id: int
    invoice_number: str
    branch_id: int
    client_id: int | None = None
    reservation_id: int | None = None
    total_amount: float
    payment_method: str
    status: str | None = None
    paid_at: datetime | None = None
    details: list[SaleDetailRead] = []


class SaleGenerate(BaseModel):
    branch_id: int
    items: list[SaleItem] | None = None
    reservation_id: int | None = None
    payment_method: str = "card"

    @model_validator(mode="after")
    def _require_source(self):
        if not self.items and not self.reservation_id:
            raise ValueError("Provide items or a reservation_id to create a sale.")
        return self

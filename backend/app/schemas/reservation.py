from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ReservationItem(BaseModel):
    variant_id: int
    quantity: int = Field(gt=0)


class ReservationCreate(BaseModel):
    branch_id: int
    pickup_code: str | None = None
    items: list[ReservationItem] = Field(min_length=1)
    notes: str | None = None


class ReservationDetailRead(ORMModel):
    id: int
    variant_id: int
    quantity: int
    unit_price: float


class ReservationRead(ORMModel):
    id: int
    client_id: int
    branch_id: int
    status: str
    pickup_code: str
    expires_at: str
    total_amount: float
    details: list[ReservationDetailRead] = []


class ReservationAction(BaseModel):
    status: str
    comment: str | None = None

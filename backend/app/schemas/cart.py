
from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.payment import PaymentRead
from app.schemas.sale import SaleRead


class CartItemIn(BaseModel):
    variant_id: int
    quantity: int = Field(gt=0)


class CartDetailRead(ORMModel):
    id: int
    variant_id: int
    quantity: int
    unit_price: float
    line_total: float


class CartRead(ORMModel):
    id: int
    branch_id: int | None
    total: float
    details: list[CartDetailRead] = []


class CartCheckout(BaseModel):
    branch_id: int | None = None
    payment_gateway: str = "mock"


class CartPurchase(BaseModel):
    branch_id: int | None = None
    payment_method: str = "card"


class PurchaseResponse(BaseModel):
    sale: SaleRead
    payment: PaymentRead

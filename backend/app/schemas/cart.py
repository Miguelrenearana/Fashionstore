
from pydantic import BaseModel, Field, model_validator

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
    # CU-20: sin esto la app movil solo puede pintar "variante 7" y un precio;
    # el nombre, la foto y la talla/color salen del modelo del catalogo.
    sku: str | None = None
    garment_id: int | None = None
    garment_name: str | None = None
    image_url: str | None = None
    size_name: str | None = None
    color_name: str | None = None
    available: int | None = None


class CartRead(ORMModel):
    id: int
    branch_id: int | None
    total: float
    items_count: int = 0
    details: list[CartDetailRead] = []

    @model_validator(mode="after")
    def _fill_items_count(self):
        if not self.items_count and self.details:
            object.__setattr__(self, "items_count", sum(d.quantity for d in self.details))
        return self


class CartCheckout(BaseModel):
    branch_id: int | None = None
    payment_gateway: str = "mock"


class CartPurchase(BaseModel):
    branch_id: int | None = None
    payment_method: str = "card"


class PurchaseResponse(BaseModel):
    sale: SaleRead
    payment: PaymentRead

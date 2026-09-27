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
    line_total: float = 0.0
    # CU-22: el historial de compras debe poder pintar el producto. Sin esto la
    # app solo recibe el variant_id y no puede mostrar nombre, foto ni talla.
    sku: str | None = None
    garment_id: int | None = None
    garment_name: str | None = None
    image_url: str | None = None
    size_name: str | None = None
    color_name: str | None = None

    @model_validator(mode="after")
    def _fill_line_total(self):
        if not self.line_total:
            object.__setattr__(self, "line_total", self.unit_price * self.quantity)
        return self


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
    # CU-22: el historial de compras necesita la fecha en que se creo el pedido
    # (paid_at es null mientras la venta sigue PENDING) y cuantas unidades llevo.
    created_at: datetime | None = None
    items_count: int = 0
    details: list[SaleDetailRead] = []

    @model_validator(mode="after")
    def _fill_items_count(self):
        if not self.items_count and self.details:
            object.__setattr__(self, "items_count", sum(d.quantity for d in self.details))
        return self


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

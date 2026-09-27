from datetime import datetime

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
    # Datos de la prenda para que el cliente no tenga que consultar el
    # catalogo por cada linea (CU-12).
    garment_id: int | None = None
    product_name: str | None = None
    size_name: str | None = None
    color_name: str | None = None
    image_url: str | None = None
    available: int = 0


class ReservationRead(ORMModel):
    id: int
    client_id: int
    branch_id: int
    status: str
    pickup_code: str
    expires_at: datetime
    total_amount: float
    details: list[ReservationDetailRead] = []
    # Alias en camelCase para clientes Flutter, que no transforman el JSON.
    items: list[ReservationDetailRead] = []
    total: float = 0
    created_at: datetime | None = None
    available_until: datetime | None = None
    reservation_code: str | None = None
    branch_name: str | None = None



class ReservationAction(BaseModel):
    status: str
    comment: str | None = None

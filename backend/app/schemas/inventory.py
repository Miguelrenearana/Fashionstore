from pydantic import BaseModel

from app.schemas.common import ORMModel


class GarmentBrief(ORMModel):
    id: int
    name: str


class InventoryVariantRead(ORMModel):
    id: int
    sku: str
    price: float
    garment: GarmentBrief | None = None
    size_name: str | None = None
    color_name: str | None = None


class InventoryRead(ORMModel):
    id: int
    branch_id: int
    variant_id: int
    quantity: int
    reserved_quantity: int
    available: int
    variant: InventoryVariantRead | None = None


class InventoryAdjust(BaseModel):
    quantity: int
    reason: str | None = None


class InventoryMovementRead(ORMModel):
    id: int
    branch_id: int
    variant_id: int
    movement_type: str
    quantity: int
    reason: str | None = None
    variant: InventoryVariantRead | None = None

from pydantic import BaseModel

from app.schemas.common import ORMModel


class InventoryRead(ORMModel):
    id: int
    branch_id: int
    variant_id: int
    quantity: int
    reserved_quantity: int
    available: int


class InventoryAdjust(BaseModel):
    quantity: int
    reason: str | None = None


class InventoryMovementRead(ORMModel):
    id: int
    variant_id: int
    movement_type: str
    quantity: int
    reason: str | None = None

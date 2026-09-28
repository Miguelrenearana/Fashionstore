from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError, ValidationError
from app.models.catalog import GarmentVariant
from app.models.inventory import Inventory
from app.models.movement import InventoryMovement, InventoryMovementType
from app.schemas.inventory import InventoryAdjust
from app.services.stock_locking import lock_stock, stock_transaction


class InventoryService:
    def list(
        self,
        db: Session,
        branch_id: int,
        variant_id: int | None = None,
    ):
        query = db.query(Inventory).filter(Inventory.branch_id == branch_id).options(
            joinedload(Inventory.variant).joinedload(GarmentVariant.garment),
            joinedload(Inventory.variant).joinedload(GarmentVariant.size),
            joinedload(Inventory.variant).joinedload(GarmentVariant.color),
        )
        if variant_id:
            query = query.filter(Inventory.variant_id == variant_id)
        return query.order_by(Inventory.variant_id).all()

    def get(self, db: Session, branch_id: int, variant_id: int) -> Inventory:
        inventory = (
            db.query(Inventory)
            .filter(Inventory.branch_id == branch_id, Inventory.variant_id == variant_id)
            .options(joinedload(Inventory.variant))
            .first()
        )
        if not inventory:
            raise NotFoundError("Inventory not found for variant.")
        return inventory

    def list_movements(
        self,
        db: Session,
        branch_id: int | None = None,
        variant_id: int | None = None,
    ):
        query = db.query(InventoryMovement).options(
            joinedload(InventoryMovement.variant).joinedload(GarmentVariant.garment),
            joinedload(InventoryMovement.variant).joinedload(GarmentVariant.size),
            joinedload(InventoryMovement.variant).joinedload(GarmentVariant.color),
        )
        if branch_id:
            query = query.filter(InventoryMovement.branch_id == branch_id)
        if variant_id:
            query = query.filter(InventoryMovement.variant_id == variant_id)
        return query.order_by(InventoryMovement.id.desc()).all()

    def adjust(self, db: Session, branch_id: int, variant_id: int, payload: InventoryAdjust) -> Inventory:
        with stock_transaction(db):
            inventory = lock_stock(db, [(branch_id, variant_id)], create_missing=True)[branch_id, variant_id]
            new_quantity = inventory.quantity + payload.quantity
            if new_quantity < 0:
                raise ValidationError("Resulting stock cannot be negative.")
            if new_quantity < inventory.reserved_quantity:
                raise ValidationError("Stock cannot be lower than the reserved quantity.")
            inventory.quantity = new_quantity
            db.add(
                InventoryMovement(
                    branch_id=branch_id,
                    variant_id=variant_id,
                    movement_type=(
                        InventoryMovementType.IN if payload.quantity >= 0 else InventoryMovementType.OUT
                    ),
                    quantity=abs(payload.quantity),
                    reason=payload.reason,
                    is_applied=True,
                )
            )
        db.refresh(inventory)
        return inventory


inventory_service = InventoryService()

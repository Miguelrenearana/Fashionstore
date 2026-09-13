from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.inventory import Inventory
from app.models.movement import InventoryMovement, InventoryMovementType


class InventoryService:
    def get(self, db: Session, branch_id: int, variant_id: int) -> Inventory:
        inventory = db.query(Inventory).filter(
            Inventory.branch_id == branch_id, Inventory.variant_id == variant_id
        ).first()
        if not inventory:
            raise NotFoundError("Inventory not found for variant.")
        return inventory

    def adjust(
        self, db: Session, branch_id: int, variant_id: int, quantity: int, reason: str | None
    ) -> Inventory:
        inventory = (
            db.query(Inventory)
            .filter(Inventory.branch_id == branch_id, Inventory.variant_id == variant_id)
            .first()
        )
        if not inventory:
            inventory = Inventory(branch_id=branch_id, variant_id=variant_id, quantity=0)
            db.add(inventory)
        inventory.quantity += quantity
        db.add(
            InventoryMovement(
                branch_id=branch_id,
                variant_id=variant_id,
                movement_type=InventoryMovementType.IN if quantity >= 0 else InventoryMovementType.OUT,
                quantity=abs(quantity),
                reason=reason,
            )
        )
        db.commit()
        db.refresh(inventory)
        return inventory


inventory_service = InventoryService()

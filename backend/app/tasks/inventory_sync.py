import logging

from app.core.database import SessionLocal
from app.models.inventory import Inventory
from app.models.movement import InventoryMovement, InventoryMovementType
from app.models.user import Branch, Employee
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)

LOW_STOCK_THRESHOLD = 5
PHONE_RE_DIGITS = 10


def sync_inventory() -> int:
    """Apply pending IN movements to inventory and flag low stock notifications."""
    db = SessionLocal()
    applied = 0
    try:
        movements = db.query(InventoryMovement).filter(
            InventoryMovement.movement_type == InventoryMovementType.IN
        ).limit(200)
        for movement in movements:
            inventory = db.query(Inventory).filter(
                Inventory.branch_id == movement.branch_id,
                Inventory.variant_id == movement.variant_id,
            ).first()
            if not inventory:
                inventory = Inventory(
                    branch_id=movement.branch_id,
                    variant_id=movement.variant_id,
                    quantity=0,
                )
                db.add(inventory)
            inventory.quantity += movement.quantity
            db.add(movement)
            db.delete(movement)
            applied += 1

        branches = db.query(Branch).all()
        for branch in branches:
            stock = db.query(Inventory).filter(
                Inventory.branch_id == branch.id,
                Inventory.quantity <= LOW_STOCK_THRESHOLD,
            ).count()
            if stock:
                for employee in db.query(Employee).filter(Employee.branch_id == branch.id):
                    if employee.user_id:
                        notification_service.notify(
                            db=db,
                            user_id=employee.user_id,
                            type="STOCK",
                            title="Stock bajo",
                            body=f"{stock} productos bajo stock en {branch.name}.",
                        )
        db.commit()
        return applied
    finally:
        db.close()

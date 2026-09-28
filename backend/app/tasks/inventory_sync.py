import logging

from app.core.database import SessionLocal
from app.models.inventory import Inventory
from app.models.movement import InventoryMovement, InventoryMovementType
from app.models.user import Branch, Employee
from app.services.notification_service import notification_service
from app.services.stock_locking import lock_stock, stock_transaction

logger = logging.getLogger(__name__)

LOW_STOCK_THRESHOLD = 5
PHONE_RE_DIGITS = 10


def sync_inventory() -> int:
    """Apply only queued IN movements once, retaining them as history."""
    db = SessionLocal()
    applied = 0
    try:
        with stock_transaction(db):
            # Claim each movement once, then acquire all stock locks in global order.
            movements = (
                db.query(InventoryMovement)
                .filter(
                    InventoryMovement.movement_type == InventoryMovementType.IN,
                    InventoryMovement.is_applied.is_(False),
                )
                .order_by(InventoryMovement.id).limit(200)
                .with_for_update(skip_locked=True).all()
            )
            stocks = lock_stock(
                db, ((m.branch_id, m.variant_id) for m in movements), create_missing=True,
            )
            for movement in movements:
                stocks[movement.branch_id, movement.variant_id].quantity += movement.quantity
                movement.is_applied = True
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

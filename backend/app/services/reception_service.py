from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.inventory import Inventory
from app.models.movement import Reception, ReceptionDetail
from app.schemas.reception import ReceptionCreate


class ReceptionService:
    def create(self, db: Session, payload: ReceptionCreate) -> Reception:
        reception = Reception(
            supplier_id=payload.supplier_id,
            branch_id=payload.branch_id,
            employee_id=payload.employee_id,
            purchase_order_ref=payload.purchase_order_ref,
            received_at=datetime.now(UTC),
            notes=payload.notes,
        )
        for item in payload.items:
            db.add(
                ReceptionDetail(
                    reception=reception,
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                    cost_price=item.cost_price,
                )
            )
            inventory = (
                db.query(Inventory)
                .filter(
                    Inventory.branch_id == payload.branch_id,
                    Inventory.variant_id == item.variant_id,
                )
                .first()
            )
            if inventory:
                inventory.quantity += item.quantity
            else:
                db.add(
                    Inventory(
                        branch_id=payload.branch_id,
                        variant_id=item.variant_id,
                        quantity=item.quantity,
                    )
                )
        db.add(reception)
        db.commit()
        db.refresh(reception)
        return reception

    def get(self, db: Session, reception_id: int) -> Reception:
        reception = db.get(Reception, reception_id)
        if not reception:
            raise NotFoundError("Reception not found.")
        return reception


reception_service = ReceptionService()

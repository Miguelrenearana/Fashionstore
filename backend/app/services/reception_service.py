from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.movement import Reception, ReceptionDetail
from app.schemas.reception import ReceptionCreate
from app.services.stock_locking import lock_stock, stock_transaction


class ReceptionService:
    def create(self, db: Session, payload: ReceptionCreate) -> Reception:
        with stock_transaction(db):
            reception = Reception(
                supplier_id=payload.supplier_id,
                branch_id=payload.branch_id,
                employee_id=payload.employee_id,
                purchase_order_ref=payload.purchase_order_ref,
                received_at=datetime.now(UTC),
                notes=payload.notes,
            )
            stocks = lock_stock(
                db, ((payload.branch_id, item.variant_id) for item in payload.items),
                create_missing=True,
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
                stocks[payload.branch_id, item.variant_id].quantity += item.quantity
            db.add(reception)
        db.refresh(reception)
        return reception

    def get(self, db: Session, reception_id: int) -> Reception:
        reception = db.get(Reception, reception_id)
        if not reception:
            raise NotFoundError("Reception not found.")
        return reception


reception_service = ReceptionService()

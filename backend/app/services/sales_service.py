from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.inventory import Inventory
from app.models.sales import Sale, SaleDetail
from app.schemas.sale import SaleGenerate


class SalesService:
    def create_sale(self, db: Session, payload: SaleGenerate, employee_id: int | None = None) -> Sale:
        if not payload.items:
            raise ValidationError("Sale must contain at least one item.")
        invoice_number = f"FAC-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        sale = Sale(
            invoice_number=invoice_number,
            branch_id=payload.branch_id,
            employee_id=employee_id,
            payment_method=payload.payment_method,
        )
        total = 0
        for item in payload.items:
            variant_id = item["variant_id"]
            quantity = item["quantity"]
            inventory = db.query(Inventory).filter(
                Inventory.branch_id == payload.branch_id,
                Inventory.variant_id == variant_id,
            ).first()
            if not inventory or inventory.available < quantity:
                raise ValidationError(f"Insufficient stock for variant {variant_id}.")
            unit_price = inventory.variant.price if inventory.variant else 0
            inventory.quantity -= quantity
            total += unit_price * quantity
            sale.details.append(
                SaleDetail(variant_id=variant_id, quantity=quantity, unit_price=unit_price)
            )
        sale.total_amount = total
        db.add(sale)
        db.commit()
        db.refresh(sale)
        return sale

    def get(self, db: Session, sale_id: int) -> Sale:
        sale = db.get(Sale, sale_id)
        if not sale:
            raise NotFoundError("Sale not found.")
        return sale


sales_service = SalesService()

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.user import Supplier


class SupplierService:
    def list(self, db: Session) -> list[Supplier]:
        return (
            db.query(Supplier)
            .filter(Supplier.is_active)
            .order_by(Supplier.company_name)
            .all()
        )

    def create(self, db: Session, payload) -> Supplier:
        item = Supplier(
            company_name=payload.company_name,
            contact_name=payload.contact_name,
            email=payload.email.lower() if payload.email else None,
            phone=payload.phone,
            address=payload.address,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update(self, db: Session, item_id: int, payload) -> Supplier:
        item = db.query(Supplier).filter(Supplier.id == item_id).first()
        if not item:
            raise NotFoundError("Supplier not found.")
        data = payload.model_dump(exclude_unset=True)
        if "email" in data and data["email"]:
            data["email"] = data["email"].lower()
        for field, value in data.items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item


supplier_service = SupplierService()

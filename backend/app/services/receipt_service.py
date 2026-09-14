from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.sales import Receipt, Sale


class ReceiptService:
    """CU-24: issue the comprobante (invoice) for a sale."""

    def generate(self, db: Session, sale: Sale, receipt_type: str = "invoice") -> Receipt:
        existing = (
            db.query(Receipt)
            .filter(Receipt.sale_id == sale.id, Receipt.type == receipt_type)
            .first()
        )
        if existing:
            return existing
        if receipt_type == "credit_note":
            identifier = f"NC-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        else:
            identifier = f"CUF-{sale.invoice_number}"
        receipt = Receipt(
            sale_id=sale.id,
            type=receipt_type,
            rnc_or_cuf=identifier,
            document_url=f"https://fashionstore.dev/receipts/{sale.invoice_number}.pdf",
        )
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
        return receipt

    def get_for_sale(self, db: Session, sale_id: int) -> Receipt | None:
        return (
            db.query(Receipt)
            .filter(Receipt.sale_id == sale_id)
            .order_by(Receipt.id.desc())
            .first()
        )


receipt_service = ReceiptService()

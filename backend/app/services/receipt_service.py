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

    def build(self, receipt: Receipt) -> dict:
        """Arma el comprobante completo (CU-24) con los datos de la venta y sus detalles."""
        sale = receipt.sale
        items = []
        for detail in sale.details if sale else []:
            variant = detail.variant
            unit_price = float(detail.unit_price)
            items.append(
                {
                    "variant_id": detail.variant_id,
                    "garment_name": variant.garment.name if variant and variant.garment else None,
                    "size_name": variant.size.name if variant and variant.size else None,
                    "color_name": variant.color.name if variant and variant.color else None,
                    "quantity": detail.quantity,
                    "unit_price": unit_price,
                    "line_total": unit_price * detail.quantity,
                }
            )
        return {
            "id": receipt.id,
            "sale_id": receipt.sale_id,
            "type": receipt.type,
            "rnc_or_cuf": receipt.rnc_or_cuf,
            "document_url": receipt.document_url,
            "created_at": receipt.created_at,
            "invoice_number": sale.invoice_number if sale else None,
            "total_amount": float(sale.total_amount) if sale else 0,
            "status": sale.status if sale else "UNKNOWN",
            "branch_name": sale.branch.name if sale and sale.branch else None,
            "items": items,
        }


receipt_service = ReceiptService()

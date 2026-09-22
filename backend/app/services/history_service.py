
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.models.catalog import GarmentVariant
from app.models.reservation import Reservation, ReservationDetail
from app.models.sales import Sale, SaleDetail


class HistoryService:
    def get_client_history(
        self,
        db: Session,
        client_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[dict], int]:
        """Obtener historial unificado de compras y reservas del cliente."""

        # Obtener ventas del cliente
        sales = self._get_client_sales(db, client_id)

        # Obtener reservas del cliente
        reservations = self._get_client_reservations(db, client_id)

        # Combinar y ordenar por fecha
        all_items = sales + reservations
        all_items.sort(key=lambda x: x["date"], reverse=True)

        # Paginación
        total = len(all_items)
        start = (page - 1) * 20
        end = start + 20
        items = all_items[start:end]

        return items, len(sales) + len(reservations)

    def _get_client_sales(self, db, client_id: int) -> list[dict]:
        sales = db.query(Sale).options(
            joinedload(Sale.details).joinedload(SaleDetail.variant)
            .joinedload(GarmentVariant.garment)
            .joinedload(GarmentVariant.size)
            .joinedload(GarmentVariant.color),
            joinedload(Sale.branch),
        ).filter(Sale.client_id == client_id).order_by(desc(Sale.created_at)).all()

        result = []
        for sale in sales:
            items = []
            for detail in sale.details:
                if detail.variant and detail.variant.garment:
                    line_total = float(detail.unit_price) * detail.quantity
                    items.append({
                        "variant_id": detail.variant_id,
                        "garment_name": detail.variant.garment.name,
                        "size_name": detail.variant.size.name if detail.variant.size else "",
                        "color_name": detail.variant.color.name if detail.variant.color else "",
                        "quantity": detail.quantity,
                        "unit_price": float(detail.unit_price),
                        "line_total": line_total,
                    })

            result.append({
                "type": "sale",
                "id": sale.id,
                "reference": sale.invoice_number,
                "date": sale.paid_at or sale.created_at,
                "total_amount": float(sale.total_amount),
                "status": sale.status,
                "branch_name": sale.branch.name if sale.branch else None,
                "items_count": len(sale.details),
                "items": items,
                "receipt_url": sale.receipts[0].document_url if sale.receipts else None,
                "receipt_type": sale.receipts[0].type if sale.receipts else None,
            })

        return result

    def _get_client_reservations(self, db, client_id: int) -> list[dict]:
        reservations = db.query(Reservation).options(
            joinedload(Reservation.details).joinedload(ReservationDetail.variant)
            .joinedload(GarmentVariant.garment)
            .joinedload(GarmentVariant.size)
            .joinedload(GarmentVariant.color),
            joinedload(Reservation.branch),
        ).filter(Reservation.client_id == client_id).order_by(desc(Reservation.created_at)).all()

        result = []
        for res in reservations:
            items = []
            for detail in res.details:
                if detail.variant and detail.variant.garment:
                    line_total = float(detail.unit_price) * detail.quantity
                    items.append({
                        "variant_id": detail.variant_id,
                        "garment_name": detail.variant.garment.name,
                        "size_name": detail.variant.size.name if detail.variant.size else "",
                        "color_name": detail.variant.color.name if detail.variant.color else "",
                        "quantity": detail.quantity,
                        "unit_price": float(detail.unit_price),
                        "line_total": line_total,
                    })

            result.append({
                "type": "reservation",
                "id": res.id,
                "reference": res.pickup_code,
                "date": res.created_at,
                "total_amount": float(res.total_amount),
                "status": res.status,
                "branch_name": res.branch.name if res.branch else None,
                "items_count": len(res.details),
                "items": items,
                "expires_at": res.expires_at,
            })

        return result


history_service = HistoryService()

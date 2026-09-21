from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.inventory import Inventory
from app.models.reservation import Reservation, ReservationHistory, ReservationStatus
from app.models.sales import Sale, SaleDetail, SaleStatus
from app.schemas.sale import SaleGenerate
from app.services.notification_service import notification_service


class SalesService:
    def create_sale(
        self,
        db: Session,
        payload: SaleGenerate,
        employee_id: int | None = None,
        client_id: int | None = None,
    ) -> Sale:
        reservation = None
        if payload.reservation_id:
            reservation = self._load_reservation(db, payload.reservation_id)
            self._validate_reservation_for_sale(db, reservation, payload.branch_id)
            items = self._reservation_items(reservation)
        elif not payload.items:
            raise ValidationError("Sale must contain at least one item.")
        else:
            items = [
                {"variant_id": it.variant_id, "quantity": it.quantity} for it in payload.items
            ]

        invoice_number = f"FAC-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
        sale = Sale(
            invoice_number=invoice_number,
            branch_id=reservation.branch_id if reservation else payload.branch_id,
            client_id=reservation.client_id if reservation else client_id,
            employee_id=employee_id,
            reservation_id=reservation.id if reservation else None,
            payment_method=payload.payment_method,
            status=SaleStatus.PENDING,
        )
        total = 0
        for item in items:
            variant_id = item["variant_id"]
            quantity = item["quantity"]
            inventory = (
                db.query(Inventory)
                .filter(
                    Inventory.branch_id == sale.branch_id,
                    Inventory.variant_id == variant_id,
                )
                .order_by(Inventory.id)
                .first()
            )
            unit_price = self._consume_inventory(
                db, sale, inventory, variant_id, quantity, reserved=reservation is not None
            )
            total += unit_price * quantity
            sale.details.append(
                SaleDetail(variant_id=variant_id, quantity=quantity, unit_price=unit_price)
            )

        sale.total_amount = total
        db.add(sale)
        if reservation:
            self._complete_reservation(db, reservation, employee_id or sale.client_id)
            client_user_id = reservation.client.user_id if reservation.client else None
            if client_user_id:
                notification_service.notify(
                    db,
                    user_id=client_user_id,
                    type="SALE",
                    title="Compra registrada",
                    body=f"Reserva {reservation.pickup_code} vendida ({sale.invoice_number}).",
                )
        db.commit()
        db.refresh(sale)
        return sale

    def get(self, db: Session, sale_id: int) -> Sale:
        sale = db.get(Sale, sale_id)
        if not sale:
            raise NotFoundError("Sale not found.")
        return sale

    @staticmethod
    def _consume_inventory(
        db: Session,
        sale: Sale,
        inventory: Inventory | None,
        variant_id: int,
        quantity: int,
        reserved: bool,
    ) -> float:
        if not inventory:
            raise ValidationError(f"Variant {variant_id} not available in this branch.")
        if reserved:
            if inventory.reserved_quantity < quantity:
                raise ConflictError(f"Reserved stock insufficient for variant {variant_id}.")
            inventory.reserved_quantity -= quantity
            inventory.quantity -= quantity
        else:
            if inventory.available < quantity:
                raise ValidationError(f"Insufficient stock for variant {variant_id}.")
            inventory.quantity -= quantity
        return inventory.variant.price if inventory.variant else 0

    @staticmethod
    def _load_reservation(db: Session, reservation_id: int) -> Reservation:
        reservation = db.get(Reservation, reservation_id)
        if not reservation:
            raise NotFoundError("Reservation not found.")
        return reservation

    def _validate_reservation_for_sale(
        self, db: Session, reservation: Reservation, branch_id: int
    ) -> None:
        if reservation.status not in (
            ReservationStatus.PENDING.value,
            ReservationStatus.PREPARED.value,
            ReservationStatus.IN_TRIAL.value,
        ):
            raise ConflictError(f"Cannot sell a reservation with status {reservation.status}.")
        if branch_id != reservation.branch_id:
            raise ConflictError("Sale branch does not match reservation branch.")

    @staticmethod
    def _reservation_items(reservation: Reservation) -> list[dict]:
        return [
            {"variant_id": d.variant_id, "quantity": d.quantity} for d in reservation.details
        ]

    @staticmethod
    def _complete_reservation(db: Session, reservation: Reservation, changed_by_user_id: int) -> None:
        reservation.history.append(
            ReservationHistory(
                from_status=reservation.status,
                to_status=ReservationStatus.COMPLETED.value,
                changed_by_user_id=changed_by_user_id,
                comment="Sale created from reservation",
            )
        )
        reservation.status = ReservationStatus.COMPLETED.value


sales_service = SalesService()

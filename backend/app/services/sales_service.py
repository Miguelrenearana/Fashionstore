from collections import Counter
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.inventory import Inventory
from app.models.reservation import Reservation, ReservationHistory, ReservationStatus
from app.models.sales import Sale, SaleDetail, SaleStatus
from app.schemas.sale import SaleGenerate
from app.services.notification_service import notification_service
from app.services.reservation_service import reservation_service
from app.services.stock_locking import lock_stock, stock_transaction


class SalesService:
    def create_sale(
        self,
        db: Session,
        payload: SaleGenerate,
        employee_id: int | None = None,
        client_id: int | None = None,
        invoice_number: str | None = None,
    ) -> Sale:
        with stock_transaction(db):
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

            invoice_number = invoice_number or f"FAC-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
            sale = Sale(
                invoice_number=invoice_number,
                branch_id=reservation.branch_id if reservation else payload.branch_id,
                client_id=reservation.client_id if reservation else client_id,
                employee_id=employee_id,
                reservation_id=reservation.id if reservation else None,
                payment_method=payload.payment_method,
                status=SaleStatus.PENDING,
            )
            quantities = Counter()
            for item in items:
                quantities[item["variant_id"]] += item["quantity"]
            stocks = lock_stock(db, ((sale.branch_id, variant_id) for variant_id in quantities))
            total = 0
            for variant_id, quantity in sorted(quantities.items()):
                inventory = stocks.get((sale.branch_id, variant_id))
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
        db.refresh(sale)
        if reservation:
            client_user_id = reservation.client.user_id if reservation.client else None
            if client_user_id:
                notification_service.notify(
                    db,
                    user_id=client_user_id,
                    type="SALE",
                    title="Compra registrada",
                    body=f"Reserva {reservation.pickup_code} vendida ({sale.invoice_number}).",
                )
        return sale

    def get(self, db: Session, sale_id: int) -> Sale:
        sale = db.get(Sale, sale_id)
        if not sale:
            raise NotFoundError("Sale not found.")
        return sale

    def reject_pending_sale(self, db: Session, sale: Sale, user_id: int) -> None:
        """Caller holds the sale lock and commits payment + stock together.

        CANCELLED is the idempotency boundary for this transition. Historical
        cancelled sales are not repaired automatically: their stock provenance
        must be reconciled separately.
        """
        if sale.status != SaleStatus.PENDING:
            return
        reservation = (
            reservation_service.lock(db, sale.reservation_id)
            if sale.reservation_id else None
        )
        quantities = Counter()
        for detail in sale.details:
            quantities[detail.variant_id] += detail.quantity
        stocks = lock_stock(db, ((sale.branch_id, v) for v in quantities))
        for variant_id, quantity in quantities.items():
            inventory = stocks.get((sale.branch_id, variant_id))
            if inventory is None:
                raise ConflictError("Cannot restore missing inventory.")
            inventory.quantity += quantity
        if reservation:
            if reservation.status != ReservationStatus.COMPLETED.value:
                raise ConflictError("Sale reservation is not completed.")
            reservation.history.append(ReservationHistory(
                from_status=reservation.status,
                to_status=ReservationStatus.CANCELLED.value,
                changed_by_user_id=user_id,
                comment="Sale payment declined; stock restored",
            ))
            reservation.status = ReservationStatus.CANCELLED.value
        # The reservation's reserved_quantity was consumed at sale creation.
        # Restoring it here would reserve the same units again.
        sale.status = SaleStatus.CANCELLED

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
            if inventory.reserved_quantity < quantity or inventory.quantity < inventory.reserved_quantity:
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
        return reservation_service.lock(db, reservation_id)

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

import secrets as _secrets
from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.reservation import (
    RESERVATION_LIFETIME_MINUTES,
    Reservation,
    ReservationDetail,
    ReservationHistory,
    ReservationStatus,
)
from app.schemas.reservation import ReservationCreate
from app.services.notification_service import notification_service
from app.services.stock_locking import lock_stock, stock_transaction


class ReservationService:
    def create(self, db: Session, client_id: int, payload: ReservationCreate) -> Reservation:
        with stock_transaction(db):
            pickup_code = payload.pickup_code or _secrets.token_hex(5).upper()
            reservation = Reservation(
                client_id=client_id,
                branch_id=payload.branch_id,
                status=ReservationStatus.PENDING.value,
                pickup_code=pickup_code,
                expires_at=datetime.now(UTC) + timedelta(minutes=RESERVATION_LIFETIME_MINUTES),
                notes=payload.notes,
            )
            quantities = Counter()
            for item in payload.items:
                quantities[item.variant_id] += item.quantity
            stocks = lock_stock(db, ((payload.branch_id, variant_id) for variant_id in quantities))
            # Validate the combined quantities under lock before reserving anything.
            for variant_id, quantity in quantities.items():
                inventory = stocks.get((payload.branch_id, variant_id))
                if not inventory or inventory.available < quantity:
                    raise ValidationError(f"Insufficient stock for variant {variant_id}.")
            total = 0
            for variant_id, quantity in sorted(quantities.items()):
                inventory = stocks[payload.branch_id, variant_id]
                inventory.reserved_quantity += quantity
                unit_price = inventory.variant.price if inventory.variant else 0
                total += unit_price * quantity
                reservation.details.append(
                    ReservationDetail(
                        variant_id=variant_id, quantity=quantity, unit_price=unit_price,
                    )
                )
            reservation.total_amount = total
            reservation.history.append(
                ReservationHistory(
                    from_status=None,
                    to_status=ReservationStatus.PENDING.value,
                    comment="Reservation created",
                )
            )
            db.add(reservation)
        db.refresh(reservation)
        return reservation

    def transition(
        self,
        db: Session,
        reservation: Reservation,
        to_status: str,
        user_id: int | None = None,
        comment: str | None = None,
    ) -> Reservation:
        with stock_transaction(db):
            reservation = self.lock(db, reservation.id)
            if to_status == ReservationStatus.EXPIRED.value and not reservation.can_expire():
                raise ConflictError("Reservation cannot be expired.")
            allowed = self._allowed_transitions(reservation.status)
            if to_status not in allowed:
                raise ConflictError(f"Cannot move {reservation.status} -> {to_status}.")
            from_status = reservation.status
            reservation.status = to_status
            reservation.history.append(
                ReservationHistory(
                    from_status=from_status,
                    to_status=to_status,
                    changed_by_user_id=user_id,
                    comment=comment,
                )
            )
            if to_status in (ReservationStatus.CANCELLED.value, ReservationStatus.EXPIRED.value):
                self._release_stock(db, reservation)
        db.refresh(reservation)
        client_user_id = reservation.client.user_id if reservation.client else None
        if client_user_id:
            notification_service.notify(
                db,
                user_id=client_user_id,
                type="RESERVATION",
                title="Estado de reserva",
                body=f"Reserva {reservation.pickup_code}: {to_status}",
            )
        return reservation

    def expire(self, db: Session, reservation: Reservation) -> Reservation:
        return self.transition(db, reservation, ReservationStatus.EXPIRED.value)

    def _release_stock(self, db: Session, reservation: Reservation) -> None:
        quantities = Counter()
        for detail in reservation.details:
            quantities[detail.variant_id] += detail.quantity
        stocks = lock_stock(db, ((reservation.branch_id, variant_id) for variant_id in quantities))
        for variant_id, quantity in quantities.items():
            inventory = stocks.get((reservation.branch_id, variant_id))
            if inventory:
                inventory.reserved_quantity = max(0, inventory.reserved_quantity - quantity)

    @staticmethod
    def lock(db: Session, reservation_id: int) -> Reservation:
        # All transitions, including sales, lock the reservation before stock.
        reservation = (
            db.query(Reservation).filter(Reservation.id == reservation_id)
            .populate_existing().with_for_update(of=Reservation).one_or_none()
        )
        if reservation is None:
            raise NotFoundError("Reservation not found.")
        return reservation

    @staticmethod
    def _allowed_transitions(status: str) -> set[str]:
        mapping = {
            ReservationStatus.PENDING.value: {
                ReservationStatus.PREPARED.value,
                ReservationStatus.CANCELLED.value,
                ReservationStatus.EXPIRED.value,
            },
            ReservationStatus.PREPARED.value: {
                ReservationStatus.IN_TRIAL.value,
                ReservationStatus.CANCELLED.value,
                ReservationStatus.EXPIRED.value,
            },
            ReservationStatus.IN_TRIAL.value: {
                ReservationStatus.CANCELLED.value,
            },
        }
        return mapping.get(status, set())


reservation_service = ReservationService()

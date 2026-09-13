import secrets as _secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ValidationError
from app.models.inventory import Inventory
from app.models.reservation import (
    RESERVATION_LIFETIME_MINUTES,
    Reservation,
    ReservationDetail,
    ReservationHistory,
    ReservationStatus,
)
from app.schemas.reservation import ReservationCreate
from app.services.notification_service import notification_service


class ReservationService:
    def create(self, db: Session, client_id: int, payload: ReservationCreate) -> Reservation:
        pickup_code = payload.pickup_code or _secrets.token_hex(5).upper()
        reservation = Reservation(
            client_id=client_id,
            branch_id=payload.branch_id,
            status=ReservationStatus.PENDING.value,
            pickup_code=pickup_code,
            expires_at=datetime.now(UTC) + timedelta(minutes=RESERVATION_LIFETIME_MINUTES),
            notes=payload.notes,
        )
        total = 0
        for item in payload.items:
            inventory = db.query(Inventory).filter(
                Inventory.branch_id == payload.branch_id,
                Inventory.variant_id == item.variant_id,
            ).first()
            if not inventory or inventory.available < item.quantity:
                raise ValidationError(f"Insufficient stock for variant {item.variant_id}.")
            inventory.reserved_quantity += item.quantity
            unit_price = inventory.variant.price if inventory.variant else 0
            total += unit_price * item.quantity
            reservation.details.append(
                ReservationDetail(
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                    unit_price=unit_price,
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
        db.commit()
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
        db.commit()
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
        if not reservation.can_expire():
            raise ConflictError("Reservation cannot be expired.")
        return self.transition(db, reservation, ReservationStatus.EXPIRED.value)

    def _release_stock(self, db: Session, reservation: Reservation) -> None:
        for detail in reservation.details:
            inventory = db.query(Inventory).filter(
                Inventory.branch_id == reservation.branch_id,
                Inventory.variant_id == detail.variant_id,
            ).first()
            if inventory:
                inventory.reserved_quantity = max(0, inventory.reserved_quantity - detail.quantity)

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

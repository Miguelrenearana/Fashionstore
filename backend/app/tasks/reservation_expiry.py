from datetime import UTC, datetime

from sqlalchemy import or_

from app.core.database import SessionLocal
from app.core.exceptions import ConflictError
from app.models.reservation import Reservation, ReservationStatus
from app.services.reservation_service import reservation_service

RESERVATION_LIFETIME_MINUTES = 30


def expire_reservations() -> int:
    """Expire PENDING/PREPARED reservations past their expires_at and notify clients."""
    now = datetime.now(UTC)
    db = SessionLocal()
    expired = 0
    try:
        reservations = db.query(Reservation).filter(
            or_(
                Reservation.status == ReservationStatus.PENDING.value,
                Reservation.status == ReservationStatus.PREPARED.value,
            ),
            Reservation.expires_at < now,
        )
        for reservation in reservations.all():
            try:
                # The service rechecks status/expiry under lock and releases stock.
                reservation_service.expire(db, reservation)
            except ConflictError:
                # Another worker or request already transitioned this reservation.
                continue
            expired += 1
        db.commit()
        return expired
    finally:
        db.close()

from datetime import UTC, datetime

from sqlalchemy import or_

from app.core.database import SessionLocal
from app.models.analytics import Notification, NotificationType
from app.models.reservation import Reservation, ReservationHistory, ReservationStatus

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
        for reservation in reservations:
            reservation.status = ReservationStatus.EXPIRED.value
            db.add(
                ReservationHistory(
                    reservation_id=reservation.id,
                    from_status=reservation.status,
                    to_status=ReservationStatus.EXPIRED.value,
                    comment="Auto-expired by scheduled job",
                )
            )
            client = reservation.client
            if client and client.user_id:
                db.add(
                    Notification(
                        user_id=client.user_id,
                        type=NotificationType.RESERVATION,
                        title="Reserva expirada",
                        body=f"Tu reserva {reservation.pickup_code} expiró por tiempo límite.",
                    )
                )
            expired += 1
        db.commit()
        return expired
    finally:
        db.close()

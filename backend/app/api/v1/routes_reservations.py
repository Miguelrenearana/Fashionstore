from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.models.reservation import Reservation
from app.models.user import Client
from app.schemas.reservation import ReservationAction, ReservationCreate, ReservationRead
from app.services.reservation_service import reservation_service

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("", response_model=ReservationRead)
def create_reservation(db: DbSession, payload: ReservationCreate, current: CurrentUser):
    client_id = _client_id_for(db, current)
    return reservation_service.create(db, client_id, payload)


@router.get("/me", response_model=list[ReservationRead])
def my_reservations(db: DbSession, current: CurrentUser):
    client_id = _client_id_for(db, current)
    return db.query(Reservation).filter(Reservation.client_id == client_id).all()


@router.patch("/{reservation_id}/status", response_model=ReservationRead)
def change_status(
    db: DbSession, reservation_id: int, payload: ReservationAction, current: CurrentUser
):
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise NotFoundError("Reservation not found.")
    return reservation_service.transition(
        db, reservation, payload.status, user_id=current.id, comment=payload.comment
    )


def _client_id_for(db, user) -> int:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if not client:
        raise NotFoundError("Client profile not found for user.")
    return client.id

from fastapi import APIRouter
from sqlalchemy.orm import joinedload, selectinload

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.catalog import Garment, GarmentVariant
from app.models.reservation import Reservation, ReservationDetail, ReservationStatus
from app.models.user import Client, Employee
from app.schemas.reservation import ReservationAction, ReservationCreate, ReservationRead
from app.services.reservation_service import reservation_service

router = APIRouter(prefix="/reservations", tags=["reservations"])

_STAFF_ROLES = ("ADMIN", "MANAGER", "CASHIER")


def _with_details(db):
    """Carga lo necesario para que el cliente no tenga que consultar el catalogo.

    Sin esto cada linea de cada reserva haria cargas perezosas (N+1).
    """
    variant = ReservationDetail.variant
    return db.query(Reservation).options(
        joinedload(Reservation.branch),
        selectinload(Reservation.details).joinedload(variant).joinedload(GarmentVariant.garment),
        selectinload(Reservation.details).joinedload(variant).joinedload(GarmentVariant.size),
        selectinload(Reservation.details).joinedload(variant).joinedload(GarmentVariant.color),
        selectinload(Reservation.details)
        .joinedload(variant)
        .joinedload(GarmentVariant.garment)
        .joinedload(Garment.images),
        selectinload(Reservation.details)
        .joinedload(variant)
        .joinedload(GarmentVariant.inventory),
    )


@router.post("", response_model=ReservationRead)
def create_reservation(db: DbSession, payload: ReservationCreate, current: CurrentUser):
    client_id = _client_id_for(db, current)
    return reservation_service.create(db, client_id, payload)


@router.get("/me", response_model=list[ReservationRead])
def my_reservations(db: DbSession, current: CurrentUser):
    client_id = _client_id_for(db, current)
    return (
        _with_details(db)
        .filter(Reservation.client_id == client_id)
        .order_by(Reservation.id.desc())
        .all()
    )


@router.get("", response_model=list[ReservationRead])
def list_reservations(db: DbSession, current: CurrentUser, status: str | None = None):
    """CU-17/18: staff view of reservations (e.g. what to prepare)."""
    user_roles = {r.name for r in current.roles}
    is_staff = bool(user_roles.intersection(_STAFF_ROLES)) or db.query(Employee).filter(
        Employee.user_id == current.id
    ).first()
    if not is_staff:
        raise ForbiddenError("Only staff can list reservations.")
    query = _with_details(db)
    if status:
        query = query.filter(Reservation.status == status.upper())
    return query.order_by(Reservation.id.desc()).all()


@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation(db: DbSession, reservation_id: int, current: CurrentUser):
    reservation = _must_get(db, reservation_id)
    _guard_owner_or_staff(db, reservation, current, allow_staff=True)
    return reservation


@router.patch("/{reservation_id}/status", response_model=ReservationRead)
def change_status(
    db: DbSession, reservation_id: int, payload: ReservationAction, current: CurrentUser
):
    reservation = _must_get(db, reservation_id)
    user_roles = {r.name for r in current.roles}
    is_staff = bool(user_roles.intersection(_STAFF_ROLES)) or db.query(Employee).filter(
        Employee.user_id == current.id
    ).first()
    if not is_staff:
        client = _client_id_for(db, current)
        if client != reservation.client_id:
            raise ForbiddenError("You cannot access this reservation.")
        if payload.status.upper() != ReservationStatus.CANCELLED.value:
            # El cliente solo puede cancelar; el resto de estados son de staff.
            raise ForbiddenError("Clients can only cancel their reservations.")
    return reservation_service.transition(
        db,
        reservation,
        payload.status.upper(),
        user_id=current.id,
        comment=payload.comment,
    )


def _client_id_for(db, user) -> int:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if not client:
        raise NotFoundError("Client profile not found for user.")
    return client.id


def _must_get(db, reservation_id: int) -> Reservation:
    reservation = _with_details(db).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise NotFoundError("Reservation not found.")
    return reservation


def _guard_owner_or_staff(db, reservation: Reservation, current: CurrentUser, allow_staff: bool):
    if allow_staff and db.query(Employee).filter(Employee.user_id == current.id).first():
        return
    owner = db.query(Client).filter(Client.user_id == current.id).first()
    if not owner or owner.id != reservation.client_id:
        raise ForbiddenError("You cannot access this reservation.")

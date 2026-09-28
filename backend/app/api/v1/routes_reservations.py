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
    is_staff, branch_id = _staff_scope(db, current)
    if not is_staff:
        raise ForbiddenError("Only staff can list reservations.")
    query = _with_details(db)
    if branch_id is not None:
        query = query.filter(Reservation.branch_id == branch_id)
    if status:
        query = query.filter(Reservation.status == status.upper())
    return query.order_by(Reservation.id.desc()).all()


@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation(db: DbSession, reservation_id: int, current: CurrentUser):
    reservation = _must_get(db, reservation_id)
    _guard_owner_or_staff(db, reservation, current)
    return reservation


@router.patch("/{reservation_id}/status", response_model=ReservationRead)
def change_status(
    db: DbSession, reservation_id: int, payload: ReservationAction, current: CurrentUser
):
    reservation = _must_get(db, reservation_id)
    is_staff, branch_id = _staff_scope(db, current)
    if not is_staff or (branch_id is not None and branch_id != reservation.branch_id):
        client = db.query(Client).filter(Client.user_id == current.id).first()
        if not client or client.id != reservation.client_id:
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


def _staff_scope(db, current: CurrentUser) -> tuple[bool, int | None]:
    """Admins see all branches; active employees see only their assigned branch."""
    if "ADMIN" in {role.name for role in current.roles}:
        return True, None
    employee = db.query(Employee).filter(
        Employee.user_id == current.id, Employee.is_active.is_(True)
    ).first()
    return (True, employee.branch_id) if employee else (False, None)


def _guard_owner_or_staff(db, reservation: Reservation, current: CurrentUser):
    is_staff, branch_id = _staff_scope(db, current)
    if is_staff and (branch_id is None or branch_id == reservation.branch_id):
        return
    owner = db.query(Client).filter(Client.user_id == current.id).first()
    if not owner or owner.id != reservation.client_id:
        raise ForbiddenError("You cannot access this reservation.")

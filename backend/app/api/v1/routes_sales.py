from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.reservation import Reservation
from app.models.sales import Sale
from app.models.user import Client, Employee
from app.schemas.receipt import ReceiptRead
from app.schemas.sale import SaleGenerate, SaleRead
from app.services.receipt_service import receipt_service
from app.services.sales_service import sales_service

router = APIRouter(prefix="/sales", tags=["sales"])

_STAFF_ROLES = ("ADMIN", "MANAGER", "CASHIER")


@router.post("", response_model=SaleRead)
def create_sale(db: DbSession, payload: SaleGenerate, current: CurrentUser):
    employee = db.query(Employee).filter(Employee.user_id == current.id).first()
    is_staff = bool({r.name for r in current.roles}.intersection(_STAFF_ROLES)) or employee is not None
    if payload.reservation_id:
        reservation = db.get(Reservation, payload.reservation_id)
        if not reservation:
            raise NotFoundError("Reservation not found.")
        owner = db.query(Client).filter(Client.user_id == current.id).first()
        if not is_staff and not (owner and owner.id == reservation.client_id):
            raise ForbiddenError("Only staff or the reservation owner can sell a reservation.")
    elif not is_staff:
        raise ForbiddenError("Only staff can register a direct sale.")
    sale = sales_service.create_sale(
        db,
        payload,
        employee_id=employee.id if employee else None,
        client_id=_client_id_for(db, current),
    )
    return sale


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(db: DbSession, sale_id: int, current: CurrentUser):
    sale = sales_service.get(db, sale_id)
    if not _can_view_sale(db, sale, current):
        raise ForbiddenError("You cannot view this sale.")
    return sale


@router.get("/{sale_id}/receipt", response_model=ReceiptRead)
def get_receipt(db: DbSession, sale_id: int, current: CurrentUser):
    """CU-24: retrieve the issued comprobante (invoice) of a sale."""
    sale = sales_service.get(db, sale_id)
    if not _can_view_sale(db, sale, current):
        raise ForbiddenError("You cannot view this sale.")
    receipt = receipt_service.get_for_sale(db, sale_id)
    if not receipt:
        raise NotFoundError("No comprobante issued for this sale yet (pay first).")
    return receipt


@router.get("", response_model=list[SaleRead])
def list_sales(db: DbSession, current: CurrentUser):
    user_roles = {r.name for r in current.roles}
    if user_roles.intersection(_STAFF_ROLES):
        return db.query(Sale).order_by(Sale.id.desc()).limit(50).all()
    client = _client_id_for(db, current)
    if not client:
        return []
    return db.query(Sale).filter(Sale.client_id == client).order_by(Sale.id.desc()).all()


def _client_id_for(db, user) -> int | None:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    return client.id if client else None


def _can_view_sale(db, sale: Sale, current: CurrentUser) -> bool:
    user_roles = {r.name for r in current.roles}
    if user_roles.intersection(_STAFF_ROLES):
        return True
    return _client_id_for(db, current) == sale.client_id


from fastapi import APIRouter, HTTPException

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import ForbiddenError
from app.models.catalog import GarmentVariant
from app.models.sales import Receipt, Sale, SaleDetail
from app.models.user import Client
from app.schemas.receipt import ReceiptPageResponse, ReceiptRead
from app.services.receipt_service import receipt_service

router = APIRouter(prefix="/receipts", tags=["receipts"])

STAFF_ROLES = {"ADMIN", "MANAGER", "CASHIER"}


def _apply_receipt_scope(db, current, query):
    """
    CU-26: A1 Cliente solo ve comprobantes de sus compras;
    A4 Cajero / A3 Encargado ven los de su sucursale; A2 ve todos.
    """
    roles = {r.name for r in current.roles}

    if roles.intersection(STAFF_ROLES):
        if "ADMIN" not in roles:
            employee = current.employee
            if not employee:
                raise ForbiddenError("El usuario no tiene una sucursal asignada.")
            return query.filter(Sale.branch_id == employee.branch_id)
        return query

    client = db.query(Client).filter(Client.user_id == current.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return query.filter(Sale.client_id == client.id)


@router.get("", response_model=ReceiptPageResponse)
def list_receipts(
    db: DbSession,
    current: CurrentUser,
    page: int = 1,
    size: int = 20,
    sale_id: int | None = None,
):
    """Listar comprobantes de las compras del cliente autenticado (CU-26)."""
    from sqlalchemy import desc
    from sqlalchemy.orm import joinedload

    query = db.query(Receipt).join(Receipt.sale).options(
        joinedload(Receipt.sale).joinedload(Sale.branch)
    )
    query = _apply_receipt_scope(db, current, query).order_by(desc(Receipt.created_at))

    if sale_id:
        query = query.filter(Receipt.sale_id == sale_id)

    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    items_data = []
    for receipt in items:
        items_data.append({
            "id": receipt.id,
            "sale_id": receipt.sale_id,
            "type": receipt.type,
            "rnc_or_cuf": receipt.rnc_or_cuf,
            "total_amount": float(receipt.sale.total_amount) if receipt.sale else 0,
            "status": receipt.sale.status if receipt.sale else "UNKNOWN",
            "created_at": receipt.created_at,
            "branch_name": receipt.sale.branch.name if receipt.sale and receipt.sale.branch else None,
        })

    return ReceiptPageResponse(
        items=items_data,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if size else 0,
    )


@router.get("/{receipt_id}", response_model=ReceiptRead)
def get_receipt(receipt_id: int, db: DbSession, current: CurrentUser):
    """Obtener detalle de un comprobante (CU-24 · CU-26)."""
    from sqlalchemy.orm import joinedload

    receipt = db.query(Receipt).options(
        joinedload(Receipt.sale).joinedload(Sale.branch),
        joinedload(Receipt.sale).joinedload(Sale.details).joinedload(SaleDetail.variant).joinedload(GarmentVariant.garment),
        joinedload(Receipt.sale).joinedload(Sale.details).joinedload(SaleDetail.variant).joinedload(GarmentVariant.size),
        joinedload(Receipt.sale).joinedload(Sale.details).joinedload(SaleDetail.variant).joinedload(GarmentVariant.color),
    ).filter(Receipt.id == receipt_id).first()

    if not receipt:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado")

    # CU-26 EXCEPCION "Acceso no autorizado"
    _apply_receipt_scope(db, current, db.query(Receipt).join(Receipt.sale).filter(Receipt.id == receipt_id)).first()

    return receipt_service.build(receipt)

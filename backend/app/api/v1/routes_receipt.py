
from fastapi import APIRouter, HTTPException

from app.core.dependencies import CurrentUser, DbSession
from app.models.catalog import GarmentVariant
from app.models.sales import Receipt, Sale, SaleDetail
from app.models.user import Client
from app.schemas.receipt import ReceiptPageResponse

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.get("", response_model=ReceiptPageResponse)
def list_receipts(
    db: DbSession,
    current: CurrentUser,
    page: int = 1,
    size: int = 20,
    sale_id: int | None = None,
):
    """Listar comprobantes del cliente autenticado."""
    client = db.query(Client).filter(Client.user_id == current.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    from sqlalchemy import desc
    from sqlalchemy.orm import joinedload

    query = db.query(Receipt).options(
        joinedload(Receipt.sale).joinedload(Sale.branch)
    ).filter(Receipt.sale_id == client.id).order_by(desc(Receipt.created_at))

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


@router.get("/{receipt_id}", response_model=dict)
def get_receipt(receipt_id: int, db: DbSession, current: CurrentUser):
    """Obtener detalle de un comprobante."""
    from sqlalchemy.orm import joinedload

    receipt = db.query(Receipt).options(
        joinedload(Receipt.sale).joinedload(Sale.branch),
        joinedload(Receipt.sale).joinedload(Sale.details).joinedload(SaleDetail.variant)
        .joinedload(GarmentVariant.garment)
        .joinedload(GarmentVariant.size)
        .joinedload(GarmentVariant.color),
    ).filter(Receipt.id == receipt_id).first()

    if not receipt:
        raise HTTPException(status_code=404, detail="Comprobante no encontrado")

    sale = receipt.sale
    items = []
    for detail in sale.details:
        items.append({
            "variant_id": detail.variant_id,
            "garment_name": detail.variant.garment.name if detail.variant and detail.variant.garment else "",
            "size_name": detail.variant.size.name if detail.variant and detail.variant.size else "",
            "color_name": detail.variant.color.name if detail.variant and detail.variant.color else "",
            "quantity": detail.quantity,
            "unit_price": float(detail.unit_price),
            "line_total": float(detail.unit_price) * detail.quantity,
        })

    return {
        "id": receipt.id,
        "sale_id": receipt.sale_id,
        "type": receipt.type,
        "rnc_or_cuf": receipt.rnc_or_cuf,
        "document_url": receipt.document_url,
        "created_at": receipt.created_at,
        "total_amount": float(sale.total_amount),
        "status": sale.status,
        "branch_name": sale.branch.name if sale.branch else None,
        "items": items,
    }


from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import CurrentUser, DbSession
from app.models.user import Client
from app.schemas.history import PurchaseHistoryResponse
from app.services.history_service import history_service

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=PurchaseHistoryResponse)
def get_purchase_history(
    db: DbSession,
    current: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """Obtener historial de compras y reservas del cliente autenticado."""

    # Obtener client_id del usuario autenticado
    client = db.query(Client).filter(Client.user_id == current.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    items, total = history_service.get_client_history(db, client.id, page, size)

    pages = (total + size - 1) // size if size else 0

    return PurchaseHistoryResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
    )

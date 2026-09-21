"""
Router de reportes (CU-33, CU-34, CU-35).

- GET /reports/indicators          -> Indicadores de ventas (query params)
- POST /reports/indicators         -> Indicadores de ventas (cuerpo JSON)
- GET /reports/stock               -> Stock bajo/agotado
- GET /reports/sales-by-period     -> Ventas por período
- GET /reports/top-products        -> Productos más vendidos
- GET /reports/low-stock           -> Stock bajo (alias)
- GET /reports/inventory-turnover  -> Rotación de inventario
- GET /reports/audit-log           -> Bitácora de auditoría
- GET /reports/consolidated        -> Reporte consolidado
"""
from datetime import UTC, datetime, timedelta
from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException

from app.core.dependencies import DbSession, CurrentUser
from app.core.exceptions import ForbiddenError
from app.models.user import User, Role
from app.schemas.report import (
    IndicatorsRequest,
    IndicatorsResponse,
    LowStockResponse,
    SalesByPeriodResponse,
    TopProductsResponse,
    InventoryTurnoverResponse,
    AuditLogPageResponse,
    ConsolidatedResponse,
)
from app.services.report_service import get_report_service
from app.services.audit_service import get_audit_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/indicators", response_model=IndicatorsResponse)
def post_indicators(
    db: DbSession,
    current: CurrentUser,
    payload: IndicatorsRequest,
):
    """Obtener indicadores de ventas (cuerpo JSON).

    Solo accesible por administradores.
    """
    _require_admin(current)
    report_service = get_report_service(db)
    return report_service.get_sales_indicators(
        start_date=payload.start_date,
        end_date=payload.end_date,
        branch_id=payload.branch_id,
    )


def _require_admin(current: CurrentUser) -> None:
    """Verificar que el usuario tiene rol ADMIN."""
    user_roles = {r.name for r in current.roles}
    if "ADMIN" not in user_roles:
        raise ForbiddenError("Solo administradores pueden acceder a reportes.")


@router.get("/indicators", response_model=IndicatorsResponse)
def get_indicators(
    db: DbSession,
    current: CurrentUser,
    start_date: datetime = Query(..., description="Fecha inicio (ISO 8601)"),
    end_date: datetime = Query(..., description="Fecha fin (ISO 8601)"),
    branch_id: Optional[int] = Query(None, description="Filtrar por sucursal"),
):
    """Obtener indicadores de ventas y stock para un período.

    Solo accesible por administradores.
    """
    _require_admin(current)
    report_service = get_report_service(db)
    return report_service.get_sales_indicators(start_date, end_date, branch_id)


@router.post("/indicators", response_model=IndicatorsResponse)
def post_indicators(
    db: DbSession,
    current: CurrentUser,
    payload: IndicatorsRequest,
):
    """Obtener indicadores de ventas y stock (cuerpo JSON).

    Solo accesible por administradores.
    """
    _require_admin(current)
    report_service = get_report_service(db)
    return report_service.get_sales_indicators(
        start_date=payload.start_date,
        end_date=payload.end_date,
        branch_id=payload.branch_id,
    )


@router.get("/stock", response_model=LowStockResponse)
def get_stock_indicators(
    db: DbSession,
    current: CurrentUser,
    branch_id: Optional[int] = Query(None, description="Filtrar por sucursal"),
    threshold: int = Query(10, ge=0, description="Umbral de stock bajo"),
):
    """Obtener indicadores de stock bajo y agotado.

    Solo accesible por administradores.
    """
    _require_admin(current)
    report_service = get_report_service(db)
    return report_service.get_stock_indicators(branch_id=branch_id, threshold=threshold)


@router.get("/sales-by-period", response_model=SalesByPeriodResponse)
def get_sales_by_period(
    db: DbSession,
    current: CurrentUser,
    period_type: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    branch_id: Optional[int] = Query(None),
):
    """Obtener ventas agrupadas por período (diario, semanal, mensual)."""
    _require_admin(current)
    report_service = get_report_service(db)
    return report_service.get_sales_by_period(
        period_type=period_type,
        start_date=start_date,
        end_date=end_date,
        branch_id=branch_id,
    )


@router.get("/top-products", response_model=TopProductsResponse)
def get_top_products(
    db: DbSession,
    current: CurrentUser,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    limit: int = Query(10, ge=1, le=100),
    branch_id: Optional[int] = Query(None),
):
    """Obtener productos más vendidos en un período."""
    _require_admin(current)
    report_service = get_report_service(db)
    return report_service.get_top_products(start_date, end_date, limit, branch_id)


@router.get("/low-stock", response_model=LowStockResponse)
def get_low_stock(
    db: DbSession,
    current: CurrentUser,
    branch_id: Optional[int] = Query(None),
    threshold: int = Query(10, ge=0),
):
    """Obtener productos con stock bajo o agotado (alias de /stock)."""
    _require_admin(current)
    report_service = get_report_service(db)
    return report_service.get_stock_indicators(branch_id=branch_id, threshold=threshold)


@router.get("/inventory-turnover", response_model=InventoryTurnoverResponse)
def get_inventory_turnover(
    db: DbSession,
    current: CurrentUser,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    branch_id: Optional[int] = Query(None),
):
    """Obtener rotación de inventario."""
    _require_admin(current)
    report_service = get_report_service(db)
    return report_service.get_inventory_turnover(start_date, end_date, branch_id)


@router.get("/audit-log", response_model=AuditLogPageResponse)
def get_audit_log(
    db: DbSession,
    current: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """Obtener bitácora de auditoría con filtros.

    Solo accesible por administradores.
    """
    _require_admin(current)
    audit_service = get_audit_service(db)
    items, total = audit_service.get_audit_log(
        page=page,
        size=size,
        user_id=user_id,
        action=action,
        entity=entity,
        start_date=start_date,
        end_date=end_date,
    )
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size,
    }


@router.get("/consolidated", response_model=ConsolidatedResponse)
def get_consolidated_report(
    db: DbSession,
    current: CurrentUser,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    branch_id: Optional[int] = Query(None),
):
    """Obtener reporte consolidado de ventas e inventario.

    Solo accesible por administradores.
    """
    _require_admin(current)
    report_service = get_report_service(db)
    return report_service.get_consolidated_report(start_date, end_date, branch_id)

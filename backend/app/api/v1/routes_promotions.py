from datetime import datetime, UTC
from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.dependencies import DbSession, CurrentUser
from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.promotions import (
    PromotionCreate, PromotionUpdate, PromotionRead, PromotionPageResponse,
    PromotionWithGarmentsRead
)
from app.schemas.common import Page
from app.services.promotion_service import promotion_service

router = APIRouter(prefix="/promotions", tags=["promotions"])


@router.post("", response_model=PromotionRead)
def create_promotion(
    db: DbSession,
    payload: PromotionCreate,
    current: CurrentUser = None
):
    """Crear nueva promoción (solo admin)."""
    try:
        result = promotion_service.create(
            db=db,
            name=payload.name,
            description=payload.description,
            discount_percent=payload.discount_percent,
            start_at=payload.start_at,
            end_at=payload.end_at,
            garment_ids=payload.garment_ids,
        )
        return result
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=PromotionPageResponse)
def list_promotions(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    active_only: bool = False,
    search: str | None = None,
):
    """Listar promociones con paginación y filtros."""
    items, total = promotion_service.list(db, page, size, active_only, search)
    return PromotionPageResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if size else 0,
    )


@router.get("/active", response_model=List[dict])
def get_active_promotions(db: DbSession):
    """Obtener promociones vigentes (para mostrar en catálogo)."""
    return promotion_service.get_active(db)


@router.get("/{promotion_id}", response_model=PromotionWithGarmentsRead)
def get_promotion(promotion_id: int, db: DbSession):
    """Obtener detalle de una promoción con sus prendas."""
    try:
        result = promotion_service.get(db, promotion_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{promotion_id}", response_model=PromotionRead)
def update_promotion(
    promotion_id: int,
    payload: PromotionUpdate,
    db: DbSession,
    current: CurrentUser = None
):
    """Actualizar promoción (solo admin)."""
    try:
        result = promotion_service.update(db, promotion_id, **payload.model_dump(exclude_unset=True))
        return result
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{promotion_id}")
def delete_promotion(promotion_id: int, db: DbSession, current: CurrentUser = None):
    """Eliminar (soft delete) una promoción."""
    try:
        promotion_service.delete(db, promotion_id)
        return {"message": "Promoción eliminada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/by-garment/{garment_id}", response_model=List[dict])
def get_promotions_by_garment(garment_id: int, db: DbSession):
    """Obtener promociones activas para una prenda específica."""
    from datetime import datetime, UTC
    from app.models.analytics import Promotion, PromotionGarment, PromotionStatus
    from sqlalchemy.orm import joinedload
    
    now = datetime.now(UTC)
    promotions = db.query(Promotion).options(
        joinedload(Promotion.garments)
    ).join(Promotion.garments).filter(
        Promotion.garments.any(id=garment_id),
        Promotion.status == PromotionStatus.ACTIVE,
        Promotion.start_at <= datetime.now(UTC),
        Promotion.end_at >= datetime.now(UTC),
    ).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "discount_percent": float(p.discount_percent),
            "start_at": p.start_at,
            "end_at": p.end_at,
        }
        for p in promotions
    ]
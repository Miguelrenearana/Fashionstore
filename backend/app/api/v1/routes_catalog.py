from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.schemas.catalog import CatalogItemRead
from app.schemas.common import Page
from app.services.catalog_service import catalog_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("", response_model=Page[CatalogItemRead])
def list_catalog(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    search: str | None = None,
):
    items, total = catalog_service.list_catalog(db, page, size, category_id, search)
    return Page[CatalogItemRead](
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if size else 0,
    )


@router.get("/{garment_id}", response_model=CatalogItemRead)
def get_catalog_item(db: DbSession, garment_id: int):
    return catalog_service.get(db, garment_id)

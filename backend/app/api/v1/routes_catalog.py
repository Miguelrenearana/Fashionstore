from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.schemas.catalog import ArConfigRead, ArVariantRead, CatalogItemRead, CategoryRead
from app.schemas.common import Page
from app.services.catalog_service import catalog_service

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(db: DbSession):
    return catalog_service.list_categories(db)


@router.get("", response_model=Page[CatalogItemRead])
def list_catalog(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    search: str | None = None,
    branch_id: int | None = None,
):
    items, total = catalog_service.list_catalog(db, page, size, category_id, search, branch_id)
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


@router.get("/{garment_id}/ar-config", response_model=ArConfigRead)
def get_ar_config(db: DbSession, garment_id: int):
    garment = catalog_service.get_ar_config(db, garment_id)
    return ArConfigRead(
        garment_id=garment.id,
        garment_name=garment.name,
        is_ar_enabled=garment.is_ar_enabled,
        variants=[
            ArVariantRead(id=v.id, sku=v.sku, size_name=v.size.name, color_name=v.color.name)
            for v in garment.variations
        ],
    )

from fastapi import APIRouter, Query

from app.core.dependencies import DbSession
from app.schemas.catalog import (
    ArConfigRead,
    ArVariantRead,
    BranchAvailabilityRead,
    BranchStockRead,
    CatalogItemRead,
    CategoryRead,
)
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
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    sizes: list[str] | None = Query(None),
    colors: list[str] | None = Query(None),
    in_stock: bool = False,
    sort_by: str | None = Query(None, pattern="^(price_asc|price_desc|name_asc|name_desc)$"),
):
    items, total = catalog_service.list_catalog(
        db,
        page,
        size,
        category_id=category_id,
        search=search,
        branch_id=branch_id,
        min_price=min_price,
        max_price=max_price,
        sizes=sizes,
        colors=colors,
        in_stock=in_stock,
        sort_by=sort_by,
    )
    return Page[CatalogItemRead](
        items=items,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size if size else 0,
    )


@router.get("/{garment_id}", response_model=CatalogItemRead)
def get_catalog_item(db: DbSession, garment_id: int, branch_id: int | None = None):
    return catalog_service.get(db, garment_id, branch_id=branch_id)


@router.get("/{garment_id}/availability", response_model=list[BranchAvailabilityRead])
def get_availability(db: DbSession, garment_id: int):
    """CU-14: disponibilidad de una prenda, desglosada por sucursal."""
    garment = catalog_service.get(db, garment_id)
    return [
        BranchAvailabilityRead(
            variant_id=v.id,
            sku=v.sku,
            price=float(v.price),
            size_name=v.size_name,
            color_name=v.color_name,
            total_available=v.available_at(),
            stock=v.stock,
            branches=[
                BranchStockRead(
                    branch_id=row.branch_id,
                    branch_name=row.branch.name if row.branch else None,
                    quantity=row.quantity,
                    reserved_quantity=row.reserved_quantity,
                    available=row.available,
                )
                for row in v.inventory
            ],
        )
        for v in garment.variations
    ]


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

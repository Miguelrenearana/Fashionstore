from fastapi import APIRouter, Depends

from app.core.dependencies import DbSession, require_roles
from app.schemas.product import GarmentCreate, GarmentRead, VariantRead
from app.services.product_service import product_service

router = APIRouter(prefix="/products", tags=["products"])

admin_manager = require_roles("ADMIN", "MANAGER")


@router.get("/{garment_id}", response_model=GarmentRead)
def get_product(db: DbSession, garment_id: int):
    return product_service.get(db, garment_id)


@router.post("", response_model=GarmentRead, dependencies=[Depends(admin_manager)])
def create_product(db: DbSession, payload: GarmentCreate):
    return product_service.create(db, payload)


@router.get("/{garment_id}/variants", response_model=list[VariantRead])
def list_variants(db: DbSession, garment_id: int):
    garment = product_service.get(db, garment_id)
    return garment.variations

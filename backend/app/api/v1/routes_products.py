from fastapi import APIRouter, Depends

from app.core.dependencies import DbSession, require_roles
from app.models.catalog import Garment
from app.schemas.product import GarmentCreate, GarmentRead, GarmentUpdate, VariantRead
from app.services.product_service import product_service

router = APIRouter(prefix="/products", tags=["products"])

admin_manager = require_roles("ADMIN", "MANAGER")


@router.get("", response_model=list[GarmentRead], dependencies=[Depends(admin_manager)])
def list_products(db: DbSession, page: int = 1, size: int = 50):
    offset = (page - 1) * size
    return db.query(Garment).offset(offset).limit(size).all()


@router.get("/{garment_id}", response_model=GarmentRead)
def get_product(db: DbSession, garment_id: int):
    return product_service.get(db, garment_id)


@router.post("", response_model=GarmentRead, dependencies=[Depends(admin_manager)])
def create_product(db: DbSession, payload: GarmentCreate):
    return product_service.create(db, payload)


@router.patch("/{garment_id}", response_model=GarmentRead, dependencies=[Depends(admin_manager)])
def update_product(db: DbSession, garment_id: int, payload: GarmentUpdate):
    return product_service.update(db, garment_id, payload)


@router.delete("/{garment_id}", status_code=204, dependencies=[Depends(admin_manager)])
def delete_product(db: DbSession, garment_id: int):
    product_service.delete(db, garment_id)


@router.get("/{garment_id}/variants", response_model=list[VariantRead])
def list_variants(db: DbSession, garment_id: int):
    garment = product_service.get(db, garment_id)
    return garment.variations
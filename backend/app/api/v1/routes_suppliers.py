from fastapi import APIRouter, Depends

from app.core.dependencies import DbSession, require_roles
from app.schemas.user import SupplierCreate, SupplierRead, SupplierUpdate
from app.services.supplier_service import supplier_service

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

manager_or_admin = require_roles("ADMIN", "MANAGER")


@router.get("", response_model=list[SupplierRead])
def list_suppliers(db: DbSession):
    return supplier_service.list(db)


@router.post(
    "",
    response_model=SupplierRead,
    dependencies=[Depends(manager_or_admin)],
)
def create_supplier(db: DbSession, payload: SupplierCreate):
    return supplier_service.create(db, payload)


@router.patch(
    "/{supplier_id}",
    response_model=SupplierRead,
    dependencies=[Depends(manager_or_admin)],
)
def update_supplier(db: DbSession, supplier_id: int, payload: SupplierUpdate):
    return supplier_service.update(db, supplier_id, payload)

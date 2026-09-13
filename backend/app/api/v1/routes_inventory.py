from fastapi import APIRouter, Depends

from app.core.dependencies import DbSession, require_roles
from app.schemas.inventory import InventoryAdjust, InventoryRead
from app.services.inventory_service import inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])

admin_manager = require_roles("ADMIN", "MANAGER")


@router.get("", response_model=list[InventoryRead])
def list_inventory(db: DbSession, branch_id: int, variant_id: int):
    item = inventory_service.get(db, branch_id, variant_id)
    return [item]


@router.patch("/adjust", response_model=InventoryRead, dependencies=[Depends(admin_manager)])
def adjust_inventory(db: DbSession, branch_id: int, variant_id: int, payload: InventoryAdjust):
    return inventory_service.adjust(db, branch_id, variant_id, payload.quantity, payload.reason)

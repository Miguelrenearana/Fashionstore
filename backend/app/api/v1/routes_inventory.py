from fastapi import APIRouter, Depends, Query

from app.core.dependencies import DbSession, require_roles
from app.schemas.inventory import InventoryAdjust, InventoryMovementRead, InventoryRead
from app.services.inventory_service import inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])

admin_manager = require_roles("ADMIN", "MANAGER")
branch_manager = require_roles("ADMIN", "MANAGER", "BRANCH_MANAGER")


@router.get("", response_model=list[InventoryRead], dependencies=[Depends(branch_manager)])
def list_inventory(
    db: DbSession,
    branch_id: int,
    variant_id: int | None = Query(None),
):
    return inventory_service.list(db, branch_id, variant_id)


@router.get(
    "/movements",
    response_model=list[InventoryMovementRead],
    dependencies=[Depends(branch_manager)],
)
def list_movements(
    db: DbSession,
    branch_id: int | None = None,
    variant_id: int | None = None,
):
    return inventory_service.list_movements(db, branch_id, variant_id)


@router.patch(
    "/{branch_id}/{variant_id}/adjust",
    response_model=InventoryRead,
    dependencies=[Depends(branch_manager)],
)
def adjust_inventory(db: DbSession, branch_id: int, variant_id: int, payload: InventoryAdjust):
    return inventory_service.adjust(db, branch_id, variant_id, payload)

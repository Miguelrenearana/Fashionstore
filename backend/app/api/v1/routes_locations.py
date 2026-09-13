from fastapi import APIRouter, Depends

from app.core.dependencies import DbSession, require_roles
from app.schemas.location import BranchCreate, BranchRead, CityRead
from app.services.location_service import location_service

router = APIRouter(prefix="/locations", tags=["locations"])

admin_manager = require_roles("ADMIN", "MANAGER")


@router.get("/cities", response_model=list[CityRead])
def list_cities(db: DbSession):
    return location_service.list_cities(db)


@router.get("/branches", response_model=list[BranchRead])
def list_branches(db: DbSession):
    return location_service.list_branches(db)


@router.post(
    "/branches",
    response_model=BranchRead,
    dependencies=[Depends(admin_manager)],
)
def create_branch(db: DbSession, payload: BranchCreate):
    return location_service.create_branch(db, payload)

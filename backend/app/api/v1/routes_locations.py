from fastapi import APIRouter, Depends, Query

from app.core.dependencies import DbSession, require_roles
from app.schemas.location import (
    BranchCreate,
    BranchRead,
    BranchUpdate,
    CityCreate,
    CityRead,
    CityUpdate,
)
from app.services.location_service import location_service

router = APIRouter(prefix="/locations", tags=["locations"])

# CU-06: A2 Administrador gestiona la red de ciudades y sucursales.
admin_only = require_roles("ADMIN")


@router.get("/cities", response_model=list[CityRead])
def list_cities(db: DbSession):
    return location_service.list_cities(db)


@router.get("/branches", response_model=list[BranchRead])
def list_branches(db: DbSession, include_inactive: bool = Query(False)):
    return location_service.list_branches(db, include_inactive=include_inactive)


@router.post(
    "/branches",
    response_model=BranchRead,
    dependencies=[Depends(admin_only)],
)
def create_branch(db: DbSession, payload: BranchCreate):
    return location_service.create_branch(db, payload)


@router.patch(
    "/branches/{branch_id}",
    response_model=BranchRead,
    dependencies=[Depends(admin_only)],
)
def update_branch(db: DbSession, branch_id: int, payload: BranchUpdate):
    return location_service.update_branch(db, branch_id, payload)


@router.post(
    "/cities",
    response_model=CityRead,
    dependencies=[Depends(admin_only)],
    status_code=201,
)
def create_city(db: DbSession, payload: CityCreate):
    return location_service.create_city(db, payload)


@router.patch(
    "/cities/{city_id}",
    response_model=CityRead,
    dependencies=[Depends(admin_only)],
)
def update_city(db: DbSession, city_id: int, payload: CityUpdate):
    return location_service.update_city(db, city_id, payload)

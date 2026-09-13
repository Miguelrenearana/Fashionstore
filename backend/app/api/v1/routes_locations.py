from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.location import BranchCreate, BranchRead, CityRead
from app.services.location_service import location_service

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/cities", response_model=list[CityRead])
def list_cities(db: DbSession):
    return location_service.list_cities(db)


@router.get("/branches", response_model=list[BranchRead])
def list_branches(db: DbSession):
    return location_service.list_branches(db)


@router.post("/branches", response_model=BranchRead)
def create_branch(db: DbSession, payload: BranchCreate, current: CurrentUser):
    return location_service.create_branch(db, payload)

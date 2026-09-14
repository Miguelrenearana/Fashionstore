from fastapi import APIRouter, Depends

from app.core.dependencies import DbSession, require_roles
from app.schemas.catalog import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    CollectionCreate,
    CollectionRead,
    CollectionUpdate,
    ColorCreate,
    ColorRead,
    SeasonCreate,
    SeasonRead,
    SizeCreate,
    SizeRead,
)
from app.services.catalog_config_service import catalog_config_service

router = APIRouter(prefix="/catalog/options", tags=["catalog-options"])

manager_or_admin = require_roles("ADMIN", "MANAGER")


@router.get("/sizes", response_model=list[SizeRead])
def list_sizes(db: DbSession):
    return catalog_config_service.list_sizes(db)


@router.get("/colors", response_model=list[ColorRead])
def list_colors(db: DbSession):
    return catalog_config_service.list_colors(db)


@router.get("/seasons", response_model=list[SeasonRead])
def list_seasons(db: DbSession):
    return catalog_config_service.list_seasons(db)


@router.get("/collections", response_model=list[CollectionRead])
def list_collections(db: DbSession):
    return catalog_config_service.list_collections(db)


@router.post(
    "/sizes",
    response_model=SizeRead,
    dependencies=[Depends(manager_or_admin)],
)
def create_size(db: DbSession, payload: SizeCreate):
    return catalog_config_service.create_size(db, payload)


@router.patch(
    "/sizes/{item_id}",
    response_model=SizeRead,
    dependencies=[Depends(manager_or_admin)],
)
def update_size(db: DbSession, item_id: int, payload: SizeCreate):
    return catalog_config_service.update_size(db, item_id, payload)


@router.post(
    "/colors",
    response_model=ColorRead,
    dependencies=[Depends(manager_or_admin)],
)
def create_color(db: DbSession, payload: ColorCreate):
    return catalog_config_service.create_color(db, payload)


@router.patch(
    "/colors/{item_id}",
    response_model=ColorRead,
    dependencies=[Depends(manager_or_admin)],
)
def update_color(db: DbSession, item_id: int, payload: ColorCreate):
    return catalog_config_service.update_color(db, item_id, payload)


@router.post(
    "/categories",
    response_model=CategoryRead,
    dependencies=[Depends(manager_or_admin)],
)
def create_category(db: DbSession, payload: CategoryCreate):
    return catalog_config_service.create_category(db, payload)


@router.patch(
    "/categories/{item_id}",
    response_model=CategoryRead,
    dependencies=[Depends(manager_or_admin)],
)
def update_category(db: DbSession, item_id: int, payload: CategoryUpdate):
    return catalog_config_service.update_category(db, item_id, payload)


@router.post(
    "/seasons",
    response_model=SeasonRead,
    dependencies=[Depends(manager_or_admin)],
)
def create_season(db: DbSession, payload: SeasonCreate):
    return catalog_config_service.create_season(db, payload)


@router.patch(
    "/seasons/{item_id}",
    response_model=SeasonRead,
    dependencies=[Depends(manager_or_admin)],
)
def update_season(db: DbSession, item_id: int, payload: SeasonCreate):
    return catalog_config_service.update_season(db, item_id, payload)


@router.post(
    "/collections",
    response_model=CollectionRead,
    dependencies=[Depends(manager_or_admin)],
)
def create_collection(db: DbSession, payload: CollectionCreate):
    return catalog_config_service.create_collection(db, payload)


@router.patch(
    "/collections/{item_id}",
    response_model=CollectionRead,
    dependencies=[Depends(manager_or_admin)],
)
def update_collection(db: DbSession, item_id: int, payload: CollectionUpdate):
    return catalog_config_service.update_collection(db, item_id, payload)

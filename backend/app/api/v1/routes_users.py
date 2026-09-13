from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.schemas.user import (
    EmployeeCreate,
    EmployeeRead,
    RoleRead,
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["users"])

admin_only = require_roles("ADMIN")


@router.get("/roles", response_model=list[RoleRead], dependencies=[Depends(admin_only)])
def list_roles(db: DbSession):
    return user_service.list_roles(db)


@router.get("", response_model=list[UserRead], dependencies=[Depends(admin_only)])
def list_users(db: DbSession, page: int = 1, size: int = 20):
    items, _ = user_service.list_users(db, page, size)
    return items


@router.get("/me", response_model=UserRead)
def me(current: CurrentUser):
    return current


@router.post("", response_model=UserRead, dependencies=[Depends(admin_only)])
def create_user(db: DbSession, payload: UserCreate):
    return user_service.create(db, payload)


@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(admin_only)])
def update_user(db: DbSession, user_id: int, payload: UserUpdate):
    return user_service.update(db, user_id, payload)


@router.post(
    "/{user_id}/employee",
    response_model=EmployeeRead,
    dependencies=[Depends(admin_only)],
)
def link_employee(db: DbSession, user_id: int, payload: EmployeeCreate):
    return user_service.link_employee(db, user_id, payload)

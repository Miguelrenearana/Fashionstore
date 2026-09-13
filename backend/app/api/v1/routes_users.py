from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["users"])

admin_only = require_roles("ADMIN")


@router.get("", response_model=list[UserRead])
def list_users(db: DbSession, _: CurrentUser, page: int = 1, size: int = 20):
    items, _ = user_service.list(db, page, size)
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

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.client import ClientProfileRead, ClientProfileUpdate
from app.services.auth_service import auth_service

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/me", response_model=ClientProfileRead)
def my_profile(db: DbSession, current: CurrentUser):
    """CU-05: read the authenticated client profile."""
    client = auth_service.get_client(db, current)
    return ClientProfileRead(
        id=client.id,
        user_id=client.user_id,
        email=current.email,
        first_name=client.first_name,
        last_name=client.last_name,
        phone=current.phone,
        birth_date=client.birth_date,
        points=client.points,
    )


@router.patch("/me", response_model=ClientProfileRead)
def update_profile(db: DbSession, current: CurrentUser, payload: ClientProfileUpdate):
    """CU-05: update the authenticated client profile."""
    client = auth_service.get_client(db, current)
    data = payload.model_dump(exclude_unset=True)
    if "first_name" in data:
        client.first_name = data["first_name"]
    if "last_name" in data:
        client.last_name = data["last_name"]
    if "birth_date" in data:
        client.birth_date = data["birth_date"]
    if "phone" in data:
        current.phone = data["phone"]
    db.commit()
    db.refresh(client)
    return ClientProfileRead(
        id=client.id,
        user_id=client.user_id,
        email=current.email,
        first_name=client.first_name,
        last_name=client.last_name,
        phone=current.phone,
        birth_date=client.birth_date,
        points=client.points,
    )

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import DbSession
from app.schemas.auth import TokenResponse
from app.schemas.common import Message
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(db: DbSession, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = auth_service.authenticate(db, form.username, form.password)
    token = auth_service.issue_token(user)
    return TokenResponse(access_token=token)


@router.post("/logout", response_model=Message)
def logout():
    # JWT stateless; client discards token.
    return Message(message="Logged out.")

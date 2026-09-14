from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import DbSession
from app.schemas.auth import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.client import ClientRegister
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


@router.post("/register", response_model=TokenResponse)
def register(db: DbSession, payload: ClientRegister):
    """CU-05: client self-registration."""
    user = auth_service.register_client(db, payload)
    token = auth_service.issue_token(user)
    return TokenResponse(access_token=token)


@router.post("/forgot-password", response_model=Message)
def forgot_password(db: DbSession, payload: ForgotPasswordRequest):
    """CU-03: request a password recovery token (mocked email)."""
    auth_service.request_password_reset(db, payload.email)
    return Message(message="Si el correo existe, recibirás un token de recuperación.")


@router.post("/reset-password", response_model=Message)
def reset_password(db: DbSession, payload: ResetPasswordRequest):
    """CU-03: validate the recovery token and set a new password."""
    auth_service.reset_password(db, payload.token, payload.password)
    return Message(message="Contraseña actualizada correctamente.")

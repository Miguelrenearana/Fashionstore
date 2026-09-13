from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")

DbSession = Annotated[Session, Depends(get_db)]


def _token_claims(token: str):
    try:
        return decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired token.") from exc


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    claims = _token_claims(token)
    user = db.get(User, int(claims.get("sub", 0)))
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*allowed_roles: str):
    def dependency(user: CurrentUser) -> User:
        user_roles = {r.name for r in user.roles}
        if not user_roles.intersection(allowed_roles):
            raise ForbiddenError("Insufficient permissions.")
        return user

    return dependency

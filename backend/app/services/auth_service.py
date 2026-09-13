from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.models.user import User


class AuthService:
    def authenticate(self, db: Session, email: str, password: str) -> User:
        user = db.query(User).filter(User.email == email.lower()).first()
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedError("Account is inactive.")
        return user

    def issue_token(self, user: User) -> str:
        return create_access_token(subject=str(user.id), roles=list(user.role_names()))


auth_service = AuthService()

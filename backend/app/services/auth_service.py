import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import Client, PasswordReset, Role, User
from app.services.notification_service import notification_service


def _utcnow() -> datetime:
    return datetime.now(UTC)


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

    def register_client(self, db: Session, payload) -> User:
        email = payload.email.lower()
        if db.query(User).filter(User.email == email).first():
            raise ForbiddenError("Email is already registered.")
        user = User(
            email=email,
            password_hash=hash_password(payload.password),
            phone=payload.phone,
            is_verified=True,
        )
        role = db.query(Role).filter(Role.name == "CLIENT").first()
        if role:
            user.roles.append(role)
        db.add(user)
        db.flush()
        db.add(Client(
            user_id=user.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            birth_date=payload.birth_date,
            points=0,
        ))
        db.commit()
        db.refresh(user)
        return user

    def request_password_reset(self, db: Session, email: str) -> str:
        """CU-03: create a reset token and notify via the (mock) gateway."""
        user = db.query(User).filter(User.email == email.lower()).first()
        token = secrets.token_urlsafe(32)
        if user:
            db.add(PasswordReset(
                user_id=user.id,
                token_hash=hashlib.sha256(token.encode()).hexdigest(),
                expires_at=_utcnow() + timedelta(minutes=30),
            ))
            db.commit()
            notification_service.notify(
                db=db,
                user_id=user.id,
                type="password_reset",
                title="Recuperación de contraseña - FashionStore",
                body=f"Usa este token para restablecer tu contraseña (válido por 30 min): {token}",
            )
        return token

    def reset_password(self, db: Session, token: str, new_password: str) -> None:
        """CU-03: validate a recovery token and set a new password."""
        digest = hashlib.sha256(token.encode()).hexdigest()
        reset = (
            db.query(PasswordReset)
            .filter(PasswordReset.token_hash == digest)
            .first()
        )
        if not reset or reset.used_at is not None:
            raise UnauthorizedError("Invalid or already used recovery token.")
        if reset.expires_at < _utcnow():
            raise UnauthorizedError("Recovery token has expired.")
        user = db.query(User).filter(User.id == reset.user_id).first()
        if not user:
            raise NotFoundError("User not found.")
        user.password_hash = hash_password(new_password)
        reset.used_at = _utcnow()
        db.commit()

    @staticmethod
    def get_client(db: Session, user: User) -> Client:
        client = db.query(Client).filter(Client.user_id == user.id).first()
        if not client:
            raise NotFoundError("Client profile not found.")
        return client


auth_service = AuthService()

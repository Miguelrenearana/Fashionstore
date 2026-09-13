from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.user import Role, User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def list(self, db: Session, page: int, size: int):
        query = db.query(User).order_by(User.id)
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return items, total

    def get(self, db: Session, user_id: int) -> User:
        user = db.get(User, user_id)
        if not user:
            raise NotFoundError("User not found.")
        return user

    def create(self, db: Session, payload: UserCreate) -> User:
        email = payload.email.lower()
        if db.query(User).filter(User.email == email).first():
            raise ConflictError("Email already registered.")
        user = User(
            email=email,
            password_hash=hash_password(payload.password),
            phone=payload.phone,
        )
        for role_name in payload.roles:
            role = db.query(Role).filter(Role.name == role_name).first()
            if role:
                user.roles.append(role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, user_id: int, payload: UserUpdate) -> User:
        user = self.get(db, user_id)
        if payload.phone is not None:
            user.phone = payload.phone
        if payload.is_active is not None:
            user.is_active = payload.is_active
        if payload.roles is not None:
            user.roles = [
                db.query(Role).filter(Role.name == name).first()
                for name in payload.roles
                if db.query(Role).filter(Role.name == name).first()
            ]
        db.commit()
        db.refresh(user)
        return user


user_service = UserService()

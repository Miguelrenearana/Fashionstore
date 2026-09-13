from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.security import hash_password
from app.models.user import Branch, Employee, Role, User
from app.schemas.user import EmployeeCreate, UserCreate, UserUpdate


class UserService:
    def list_users(self, db: Session, page: int, size: int):
        query = db.query(User).order_by(User.id)
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return items, total

    def get(self, db: Session, user_id: int) -> User:
        user = db.get(User, user_id)
        if not user:
            raise NotFoundError("User not found.")
        return user

    def list_roles(self, db: Session) -> list[Role]:
        return db.query(Role).order_by(Role.id).all()

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
            if not role:
                raise ValidationError(f"Role '{role_name}' does not exist.")
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
            roles = []
            for name in payload.roles:
                role = db.query(Role).filter(Role.name == name).first()
                if not role:
                    raise ValidationError(f"Role '{name}' does not exist.")
                roles.append(role)
            user.roles = roles
        db.commit()
        db.refresh(user)
        return user

    def link_employee(self, db: Session, user_id: int, payload: EmployeeCreate) -> Employee:
        user = self.get(db, user_id)
        if user.employee:
            raise ConflictError("User already linked to an employee profile.")
        if not db.get(Branch, payload.branch_id):
            raise NotFoundError("Branch not found.")
        hire_date = None
        if payload.hire_date:
            try:
                hire_date = date.fromisoformat(payload.hire_date)
            except ValueError as exc:
                raise ValidationError("hire_date must be ISO format (YYYY-MM-DD).") from exc
        employee = Employee(
            user_id=user.id,
            branch_id=payload.branch_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            hire_date=hire_date,
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee


user_service = UserService()

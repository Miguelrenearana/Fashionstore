from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, SoftDeleteMixin, TimestampMixin


class Role(Base, TimestampMixin):
    __tablename__ = "rol"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(200))

    users = relationship("User", secondary="usuario_rol", back_populates="roles")


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    roles = relationship("Role", secondary="usuario_rol", back_populates="users")
    employee = relationship("Employee", back_populates="user", uselist=False)

    def role_names(self) -> set[str]:
        return {r.name for r in self.roles}


class UserRole(Base, TimestampMixin):
    __tablename__ = "usuario_rol"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_usuario_rol"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("usuario.id", ondelete="CASCADE"))
    role_id: Mapped[int] = mapped_column(ForeignKey("rol.id", ondelete="CASCADE"))


class City(Base, TimestampMixin):
    __tablename__ = "ciudad"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)

    branches = relationship("Branch", back_populates="city")


class Branch(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "sucursal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("ciudad.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))

    city = relationship("City", back_populates="branches")
    employees = relationship("Employee", back_populates="branch")
    inventory = relationship("Inventory", back_populates="branch")
    sales = relationship("Sale", back_populates="branch")


class Employee(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "empleado"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    branch_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)

    user = relationship("User", back_populates="employee")
    branch = relationship("Branch", back_populates="employees")


class Supplier(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "proveedor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(String(255))

    receptions = relationship("Reception", back_populates="supplier")


class Client(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "cliente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user = relationship("User")
    carts = relationship("Cart", back_populates="client")
    reservations = relationship("Reservation", back_populates="client")


class PasswordReset(Base, TimestampMixin):
    """Recovery tokens for CU-03 (Recuperar contrasena)."""

    __tablename__ = "password_reset"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

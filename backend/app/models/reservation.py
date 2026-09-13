from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin

RESERVATION_LIFETIME_MINUTES = 30


class ReservationStatus(str, Enum):
    PENDING = "PENDING"
    PREPARED = "PREPARED"
    IN_TRIAL = "IN_TRIAL"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class Reservation(Base, TimestampMixin):
    __tablename__ = "reserva"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("cliente.id"), nullable=False)
    branch_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=ReservationStatus.PENDING, nullable=False)
    pickup_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    client = relationship("Client", back_populates="reservations")
    details = relationship("ReservationDetail", back_populates="reservation", cascade="all, delete-orphan")
    history = relationship("ReservationHistory", back_populates="reservation", cascade="all, delete-orphan")

    def can_expire(self) -> bool:
        return (
            self.status in (ReservationStatus.PENDING.value, ReservationStatus.PREPARED.value)
            and self.expires_at.replace(tzinfo=UTC) < datetime.now(UTC)
        )


class ReservationDetail(Base, TimestampMixin):
    __tablename__ = "reserva_detalle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reserva.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    reservation = relationship("Reservation", back_populates="details")
    variant = relationship("GarmentVariant")


class ReservationHistory(Base, TimestampMixin):
    __tablename__ = "reserva_historial"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reserva.id", ondelete="CASCADE"), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    comment: Mapped[str | None] = mapped_column(Text)

    reservation = relationship("Reservation", back_populates="history")

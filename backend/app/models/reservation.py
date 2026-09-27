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
    branch = relationship("Branch")
    details = relationship("ReservationDetail", back_populates="reservation", cascade="all, delete-orphan")
    history = relationship("ReservationHistory", back_populates="reservation", cascade="all, delete-orphan")

    def can_expire(self) -> bool:
        return (
            self.status in (ReservationStatus.PENDING.value, ReservationStatus.PREPARED.value)
            and self.expires_at.replace(tzinfo=UTC) < datetime.now(UTC)
        )

    # --- Alias en camelCase que espera el cliente movil (CU-12) ---
    @property
    def items(self) -> list["ReservationDetail"]:
        return self.details

    @property
    def total(self) -> float:
        return float(self.total_amount or 0)

    @property
    def available_until(self) -> datetime:
        return self.expires_at

    @property
    def reservation_code(self) -> str:
        return self.pickup_code

    @property
    def branch_name(self) -> str | None:
        return self.branch.name if self.branch else None


class ReservationDetail(Base, TimestampMixin):
    __tablename__ = "reserva_detalle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reserva.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    reservation = relationship("Reservation", back_populates="details")
    variant = relationship("GarmentVariant")

    # --- Datos derivados para el cliente (CU-12) ---
    @property
    def garment_id(self) -> int | None:
        return self.variant.garment_id if self.variant else None

    @property
    def product_name(self) -> str | None:
        if self.variant is None or self.variant.garment is None:
            return None
        return self.variant.garment.name

    @property
    def size_name(self) -> str | None:
        return self.variant.size.name if self.variant and self.variant.size else None

    @property
    def color_name(self) -> str | None:
        return self.variant.color.name if self.variant and self.variant.color else None

    @property
    def image_url(self) -> str | None:
        if self.variant is None or self.variant.garment is None:
            return None
        images = self.variant.garment.images
        if not images:
            return None
        primary = next((i for i in images if i.is_primary), images[0])
        return primary.url

    @property
    def available(self) -> int:
        branch_id = self.reservation.branch_id if self.reservation else None
        return self.variant.available_at(branch_id) if self.variant else 0


class ReservationHistory(Base, TimestampMixin):
    __tablename__ = "reserva_historial"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reserva.id", ondelete="CASCADE"), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    changed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    comment: Mapped[str | None] = mapped_column(Text)

    reservation = relationship("Reservation", back_populates="history")

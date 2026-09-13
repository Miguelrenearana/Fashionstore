from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, SoftDeleteMixin, TimestampMixin


class BrowsingHistory(Base, TimestampMixin):
    __tablename__ = "historial_navegacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("cliente.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id"), nullable=False)
    view_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    variant = relationship("GarmentVariant")


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recomendacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("cliente.id", ondelete="CASCADE"), nullable=False)
    source_variant_id: Mapped[int | None] = mapped_column(ForeignKey("prenda_variante.id"))
    suggested_variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id"), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    is_consumed: Mapped[bool] = mapped_column(default=False, nullable=False)

    suggested_variant = relationship("GarmentVariant")


class PromotionStatus:
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"


class Promotion(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "promocion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(300))
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=PromotionStatus.ACTIVE, nullable=False)

    garments = relationship("Garment", secondary="promocion_prenda", back_populates="promotions")


class PromotionGarment(Base, TimestampMixin):
    __tablename__ = "promocion_prenda"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    promotion_id: Mapped[int] = mapped_column(ForeignKey("promocion.id", ondelete="CASCADE"), nullable=False)
    garment_id: Mapped[int] = mapped_column(ForeignKey("prenda.id", ondelete="CASCADE"), nullable=False)


class NotificationType:
    RESERVATION = "RESERVATION"
    STOCK = "STOCK"
    PROMOTION = "PROMOTION"
    SYSTEM = "SYSTEM"


class Notification(Base, TimestampMixin):
    __tablename__ = "notificacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    body: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)

    user = relationship("User")


class AuditLog(Base, TimestampMixin):
    __tablename__ = "bitacora_sistema"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    entity: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    metadata_json: Mapped[str | None] = mapped_column(String(1000))

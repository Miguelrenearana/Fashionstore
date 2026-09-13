from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin


class Reception(Base, TimestampMixin):
    __tablename__ = "recepcion_producto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("proveedor.id"), nullable=False)
    branch_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("empleado.id"), nullable=False)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    purchase_order_ref: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)

    supplier = relationship("Supplier", back_populates="receptions")
    details = relationship("ReceptionDetail", back_populates="reception", cascade="all, delete-orphan")


class ReceptionDetail(Base, TimestampMixin):
    __tablename__ = "recepcion_producto_detalle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reception_id: Mapped[int] = mapped_column(ForeignKey("recepcion_producto.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    reception = relationship("Reception", back_populates="details")
    variant = relationship("GarmentVariant")


class InventoryMovementType:
    IN = "IN"
    OUT = "OUT"


class InventoryMovement(Base, TimestampMixin):
    __tablename__ = "movimiento_inventario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id"), nullable=False)
    movement_type: Mapped[str] = mapped_column(String(10), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(120))

    variant = relationship("GarmentVariant")

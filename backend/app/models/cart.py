from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin


class Cart(Base, TimestampMixin):
    __tablename__ = "carrito"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("cliente.id", ondelete="CASCADE"), nullable=False)
    branch_id: Mapped[int | None] = mapped_column(ForeignKey("sucursal.id"))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    client = relationship("Client", back_populates="carts")
    details = relationship("CartDetail", back_populates="cart", cascade="all, delete-orphan")

    @property
    def total(self) -> Decimal:
        return sum((d.line_total for d in self.details), Decimal("0.00"))


class CartDetail(Base, TimestampMixin):
    __tablename__ = "carrito_detalle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carrito.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    cart = relationship("Cart", back_populates="details")
    variant = relationship("GarmentVariant")

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity

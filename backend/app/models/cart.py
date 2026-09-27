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

    @property
    def items_count(self) -> int:
        return sum(d.quantity for d in self.details)


class CartDetail(Base, TimestampMixin):
    __tablename__ = "carrito_detalle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cart_id: Mapped[int] = mapped_column(Integer, ForeignKey("carrito.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[int] = mapped_column(Integer, ForeignKey("prenda_variante.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    cart = relationship("Cart", back_populates="details")
    variant = relationship("GarmentVariant")

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity

    # Campos derivados para que el carrito se pueda pintar sin una segunda
    # llamada al catalogo (la app movil los consume en la lista).
    @property
    def sku(self) -> str | None:
        return self.variant.sku if self.variant else None

    @property
    def garment_name(self) -> str | None:
        return self.variant.garment.name if self.variant and self.variant.garment else None

    @property
    def image_url(self) -> str | None:
        if not self.variant or not self.variant.garment:
            return None
        images = self.variant.garment.images
        return images[0].url if images else None

    @property
    def size_name(self) -> str | None:
        return self.variant.size.name if self.variant and self.variant.size else None

    @property
    def color_name(self) -> str | None:
        return self.variant.color.name if self.variant and self.variant.color else None

    @property
    def available(self) -> int | None:
        if not self.variant:
            return None
        return self.variant.available_at(self.cart.branch_id if self.cart else None)

    @property
    def garment_id(self) -> int | None:
        return self.variant.garment_id if self.variant else None

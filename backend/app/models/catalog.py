from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, SoftDeleteMixin, TimestampMixin


class Category(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "categoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    garments = relationship("Garment", back_populates="category")


class Size(Base, TimestampMixin):
    __tablename__ = "talla"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    variations = relationship("GarmentVariant", back_populates="size")


class Color(Base, TimestampMixin):
    __tablename__ = "color"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    hex_code: Mapped[str | None] = mapped_column(String(7))

    variations = relationship("GarmentVariant", back_populates="color")


class Season(Base, TimestampMixin):
    __tablename__ = "temporada"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    collections = relationship("Collection", back_populates="season")


class Collection(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "coleccion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("temporada.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    launch_year: Mapped[int] = mapped_column(Integer, nullable=False)

    season = relationship("Season", back_populates="collections")
    garments = relationship("Garment", back_populates="collection")


class Garment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "prenda"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categoria.id"), nullable=False)
    collection_id: Mapped[int | None] = mapped_column(ForeignKey("coleccion.id"))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_ar_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    category = relationship("Category", back_populates="garments")
    collection = relationship("Collection", back_populates="garments")
    variations: Mapped[list["GarmentVariant"]] = relationship(
        back_populates="garment", cascade="all, delete-orphan"
    )
    images: Mapped[list["GarmentImage"]] = relationship(
        back_populates="garment", cascade="all, delete-orphan"
    )
    promotions = relationship("Promotion", secondary="promocion_prenda", back_populates="garments")

    @property
    def variants(self):
        return self.variations

    @property
    def min_price(self) -> Decimal:
        prices = [v.price for v in self.variations]
        return min(prices) if prices else self.base_price

    @property
    def in_stock(self) -> bool:
        return any(v.available > 0 for v in self.variations)


class GarmentVariant(Base, TimestampMixin):
    __tablename__ = "prenda_variante"

    # _stock_override / _available_override son estado de la respuesta, no columnas.
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    garment_id: Mapped[int] = mapped_column(ForeignKey("prenda.id", ondelete="CASCADE"), nullable=False)
    size_id: Mapped[int] = mapped_column(ForeignKey("talla.id"), nullable=False)
    color_id: Mapped[int] = mapped_column(ForeignKey("color.id"), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    garment = relationship("Garment", back_populates="variations")
    size = relationship("Size", back_populates="variations")
    color = relationship("Color", back_populates="variations")
    # Una fila de inventario por cada sucursal donde existe la variante.
    inventory = relationship("Inventory", back_populates="variant")

    # Valores de inventario resueltos por el servicio de catálogo para una
    # sucursal concreta. No son columnas: son estado de la respuesta actual.
    _stock_override: int | None = None
    _available_override: int | None = None

    def set_stock(self, stock: int, available: int) -> None:
        """Fija el inventario resuelto por el servicio (respeta branch_id)."""
        self._stock_override = stock
        self._available_override = available

    @property
    def stock(self) -> int:
        """Unidades fisicas en inventario (CU-14)."""
        if self._stock_override is not None:
            return self._stock_override
        return sum(r.quantity for r in self.inventory)

    @property
    def available(self) -> int:
        """Unidades disponibles tras descontar reservas (CU-14)."""
        if self._available_override is not None:
            return self._available_override
        return self.available_at()

    def available_at(self, branch_id: int | None = None) -> int:
        """Unidades disponibles de la variante, opcionalmente en una sucursal (CU-14)."""
        rows = self.inventory
        if branch_id is not None:
            rows = [r for r in rows if r.branch_id == branch_id]
        return sum(r.available for r in rows)

    @property
    def size_name(self) -> str | None:
        return self.size.name if self.size else None

    @property
    def color_name(self) -> str | None:
        return self.color.name if self.color else None


class GarmentImage(Base, TimestampMixin):
    __tablename__ = "prenda_imagen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    garment_id: Mapped[int] = mapped_column(ForeignKey("prenda.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    garment = relationship("Garment", back_populates="images")


class Model3D(Base, TimestampMixin):
    __tablename__ = "modelo3d"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    garment_id: Mapped[int] = mapped_column(ForeignKey("prenda.id", ondelete="CASCADE"), nullable=False)
    asset_url: Mapped[str] = mapped_column(String(500), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

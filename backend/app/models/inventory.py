from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin


class Inventory(Base, TimestampMixin):
    __tablename__ = "inventario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    variant = relationship("GarmentVariant", back_populates="inventory")

    @property
    def available(self) -> int:
        return self.quantity - self.reserved_quantity


class ProductEmbedding(Base, TimestampMixin):
    __tablename__ = "product_embeddings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id", ondelete="CASCADE"), nullable=False)
    model: Mapped[str] = mapped_column(default="all-MiniLM-L6-v2", nullable=False)
    embedding = mapped_column(Vector(384), nullable=False)

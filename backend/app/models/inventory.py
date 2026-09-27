from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin


class Inventory(Base, TimestampMixin):
    __tablename__ = "inventario"
    __table_args__ = (
        # Una sola fila de inventario por variante y sucursal. Sin esto, dos
        # altas para la misma pareja duplican el stock y rompen CU-14.
        UniqueConstraint("variant_id", "branch_id", name="uq_inventario_variante_sucursal"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    variant = relationship("GarmentVariant", back_populates="inventory")
    branch = relationship("Branch", back_populates="inventory")

    @property
    def available(self) -> int:
        return self.quantity - self.reserved_quantity


class ProductEmbedding(Base, TimestampMixin):
    __tablename__ = "product_embeddings"
    __table_args__ = (
        # VectorStore.hace UPSERT con ON CONFLICT (variant_id); sin esta
        # restriccion el backfill de embeddings revienta.
        UniqueConstraint("variant_id", name="uq_product_embeddings_variant_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id", ondelete="CASCADE"), nullable=False)
    model: Mapped[str] = mapped_column(default="all-MiniLM-L6-v2", nullable=False)
    embedding = mapped_column(Vector(384), nullable=False)

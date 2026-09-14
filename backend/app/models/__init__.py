from datetime import datetime

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SoftDeleteMixin:
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# Re-export modelos para Alembic (autogenerate) y app.
from app.models.analytics import (  # noqa: E402, F401
    AuditLog,
    BrowsingHistory,
    Notification,
    Promotion,
    PromotionGarment,
    Recommendation,
)
from app.models.cart import Cart, CartDetail  # noqa: E402, F401
from app.models.catalog import (  # noqa: E402, F401
    Category,
    Collection,
    Color,
    Garment,
    GarmentImage,
    GarmentVariant,
    Model3D,
    Season,
    Size,
)
from app.models.inventory import Inventory, ProductEmbedding  # noqa: E402, F401
from app.models.movement import (  # noqa: E402, F401
    InventoryMovement,
    Reception,
    ReceptionDetail,
)
from app.models.reservation import (  # noqa: E402, F401
    Reservation,
    ReservationDetail,
    ReservationHistory,
)
from app.models.sales import Payment, Receipt, Sale, SaleDetail  # noqa: E402, F401
from app.models.user import (  # noqa: E402, F401
    Branch,
    City,
    Client,
    Employee,
    PasswordReset,
    Role,
    Supplier,
    User,
    UserRole,
)

__all__ = ["Base", "TimestampMixin", "SoftDeleteMixin"]

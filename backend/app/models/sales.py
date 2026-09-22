from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base, TimestampMixin


class SaleStatus:
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class Sale(Base, TimestampMixin):
    __tablename__ = "venta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("cliente.id"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("sucursal.id"), nullable=False)
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("empleado.id"))
    reservation_id: Mapped[int | None] = mapped_column(ForeignKey("reserva.id"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=SaleStatus.PENDING, nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    details = relationship("SaleDetail", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sale")
    reservation = relationship("Reservation")
    client = relationship("Client")
    branch = relationship("Branch", back_populates="sales")


class SaleDetail(Base, TimestampMixin):
    __tablename__ = "venta_detalle"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("venta.id", ondelete="CASCADE"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("prenda_variante.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    sale = relationship("Sale", back_populates="details")
    variant = relationship("GarmentVariant")


class SalePaymentStatus:
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"
    REFUNDED = "REFUNDED"
    TIMEOUT = "TIMEOUT"


class Payment(Base, TimestampMixin):
    __tablename__ = "pago"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gateway_reference: Mapped[str | None] = mapped_column(String(100), unique=True)
    sale_id: Mapped[int | None] = mapped_column(ForeignKey("venta.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="BOB", nullable=False)
    method: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=SalePaymentStatus.PENDING, nullable=False)

    # Static QR Gateway fields
    qr_payload: Mapped[str | None] = mapped_column(String(500), nullable=True)
    qr_svg: Mapped[str | None] = mapped_column(String, nullable=True)
    qr_png_base64: Mapped[str | None] = mapped_column(String, nullable=True)
    qr_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    qr_webhook_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    qr_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    qr_verification_method: Mapped[str] = mapped_column(String(20), default="polling", nullable=False)  # polling, webhook
    qr_manually_marked_paid: Mapped[bool] = mapped_column(default=False, nullable=False)
    qr_webhook_payload: Mapped[str | None] = mapped_column(String, nullable=True)

    sale = relationship("Sale", back_populates="payments")


class Receipt(Base, TimestampMixin):
    __tablename__ = "comprobante"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("venta.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # invoice | credit_note
    rnc_or_cuf: Mapped[str | None] = mapped_column(String(60))
    document_url: Mapped[str | None] = mapped_column(String(500))

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal


class PaymentStatus:
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"
    REFUNDED = "REFUNDED"
    TIMEOUT = "TIMEOUT"


@dataclass
class PaymentRequest:
    order_reference: str
    amount: Decimal
    currency: str = "BOB"
    customer_email: str | None = None
    description: str | None = None
    meta: dict = field(default_factory=dict)


@dataclass
class PaymentResult:
    gateway: str
    reference: str
    status: str
    payment_url: str | None = None
    raw: dict = field(default_factory=dict)

    @property
    def succeeded(self) -> bool:
        return self.status == PaymentStatus.COMPLETED


@dataclass
class PaymentStatusResult:
    reference: str
    status: str
    raw: dict = field(default_factory=dict)


def utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()

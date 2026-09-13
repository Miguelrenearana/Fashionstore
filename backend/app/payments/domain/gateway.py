from abc import ABC, abstractmethod
from decimal import Decimal

from app.payments.domain.entities import (
    PaymentRequest,
    PaymentResult,
    PaymentStatusResult,
)


class PaymentGateway(ABC):
    name: str

    @abstractmethod
    def create_payment(self, request: PaymentRequest) -> PaymentResult:
        """Create a payment in the gateway and return intent/URL."""

    @abstractmethod
    def get_status(self, reference: str) -> PaymentStatusResult:
        """Query the current status of a payment."""

    @abstractmethod
    def refund(self, reference: str, amount: Decimal | None = None) -> PaymentResult:
        """Refund (full or partial) a completed payment."""

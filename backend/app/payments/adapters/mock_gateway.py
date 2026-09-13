import uuid
from decimal import Decimal

from app.core.config import settings
from app.payments.domain.entities import (
    PaymentRequest,
    PaymentResult,
    PaymentStatus,
    PaymentStatusResult,
)
from app.payments.domain.gateway import PaymentGateway


class MockGateway(PaymentGateway):
    """Deterministic mock gateway for development/demo.

    Scenarios can be forced via the last characters of the customer email:
      *@mock.{success|declined|timeout|refund}  (default: success)
    """

    name = "mock"

    def _scenario(self, email: str | None) -> str:
        if email and ".mock." in email:
            return email.split(".mock.")[-1].lower()
        return "success"

    def create_payment(self, request: PaymentRequest) -> PaymentResult:
        scenario = self._scenario(request.customer_email)
        reference = f"mock_{uuid.uuid4().hex[:16]}"
        status_map = {
            "declined": PaymentStatus.DECLINED,
            "timeout": PaymentStatus.TIMEOUT,
            "success": PaymentStatus.PENDING,
        }
        status = status_map.get(scenario, PaymentStatus.PENDING)
        payment_url = f"{settings.base_url_app}/payments/mock/{reference}"
        return PaymentResult(
            gateway=self.name,
            reference=reference,
            status=status,
            payment_url=payment_url,
            raw={"scenario": scenario, "callback_url": f"{payment_url}/callback"},
        )

    def get_status(self, reference: str) -> PaymentStatusResult:
        status = PaymentStatus.COMPLETED
        if reference.split("_") and "declined" in reference:
            status = PaymentStatus.DECLINED
        return PaymentStatusResult(reference=reference, status=status)

    def refund(self, reference: str, amount: Decimal | None = None) -> PaymentResult:
        return PaymentResult(
            gateway=self.name,
            reference=reference,
            status=PaymentStatus.REFUNDED,
            raw={"amount": str(amount) if amount else None},
        )

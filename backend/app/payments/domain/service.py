from app.payments.domain.entities import PaymentRequest, PaymentResult, PaymentStatusResult
from app.payments.domain.gateway import PaymentGateway


class PaymentService:
    """High-level payment orchestration over the configured gateway."""

    def __init__(self, gateway: PaymentGateway):
        self._gateway = gateway

    @property
    def gateway(self) -> PaymentGateway:
        return self._gateway

    def pay(self, order_reference: str, amount, currency: str = "BOB", **extra) -> PaymentResult:
        return self._gateway.create_payment(
            PaymentRequest(
                order_reference=order_reference,
                amount=amount,
                currency=currency,
                customer_email=extra.get("customer_email"),
                description=extra.get("description"),
            )
        )

    def status(self, reference: str) -> PaymentStatusResult:
        return self._gateway.get_status(reference)

    def refund(self, reference: str) -> PaymentResult:
        return self._gateway.refund(reference)

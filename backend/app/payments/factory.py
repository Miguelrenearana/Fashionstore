from functools import lru_cache

from app.core.config import settings
from app.core.exceptions import PaymentError
from app.payments.adapters.mock_gateway import MockGateway
from app.payments.adapters.pagosnet_gateway import PagosNetGateway
from app.payments.domain.gateway import PaymentGateway
from app.payments.domain.service import PaymentService


def build_gateway() -> PaymentGateway:
    selected = settings.payment_gateway.lower()
    if selected == "mock":
        return MockGateway()
    if selected == "pagosnet":
        return PagosNetGateway()
    raise PaymentError(f"Unknown payment gateway: {settings.payment_gateway}")


@lru_cache
def get_payment_service() -> PaymentService:
    return PaymentService(build_gateway())

import hashlib
import hmac
import uuid
from decimal import Decimal

import httpx

from app.core.config import settings
from app.core.exceptions import PaymentError
from app.payments.domain.entities import (
    PaymentRequest,
    PaymentResult,
    PaymentStatus,
    PaymentStatusResult,
)
from app.payments.domain.gateway import PaymentGateway


class PagosNetGateway(PaymentGateway):
    """Adapter for PagosNet (Red Enlace / ASOBAN) sandbox.

    Mapeo de estados PagosNet -> dominio:
      PE (pendiente)  -> PENDING
      CO (confirmada) -> COMPLETED
      CA (cancelada)  -> CANCELLED/DECLINED

    Se activa solo con credenciales sandbox (PAGOSNET_API_KEY/
    PAGOSNET_ENCRYPTION_KEY). Sin credenciales cae a PaymentError.
    """

    name = "pagosnet"

    def __init__(self) -> None:
        if not settings.pagosnet_api_key or not settings.pagosnet_encryption_key:
            raise PaymentError(
                "PagosNet sandbox requires PAGOSNET_API_KEY and PAGOSNET_ENCRYPTION_KEY."
            )
        self._api_key = settings.pagosnet_api_key
        self._encryption_key = settings.pagosnet_encryption_key
        self._base_url = settings.pagosnet_base_url.rstrip("/")

    def _signature(self, payload: str) -> str:
        return hmac.new(
            self._encryption_key.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

    def _post(self, path: str, payload: dict) -> dict:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self._api_key,
            "X-Signature": self._signature(path),
        }
        try:
            resp = httpx.post(f"{self._base_url}{path}", json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise PaymentError(f"PagosNet request failed: {exc}") from exc
        return resp.json()

    def create_payment(self, request: PaymentRequest) -> PaymentResult:
        body = {
            "merchant_payment_code": request.order_reference,
            "amount_total": str(request.amount),
            "currency_code": request.currency,
            "customer": {"email": request.customer_email or ""},
            "description": request.description or "",
        }
        data = self._post("/transactions", body)
        status = self._map_status(data.get("status", "PE"))
        return PaymentResult(
            gateway=self.name,
            reference=str(data.get("id") or data.get("reference") or uuid.uuid4().hex),
            status=status,
            payment_url=data.get("payment_url"),
            raw=data,
        )

    def get_status(self, reference: str) -> PaymentStatusResult:
        resp = httpx.get(
            f"{self._base_url}/transactions/{reference}",
            headers={"X-API-Key": self._api_key},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return PaymentStatusResult(
            reference=reference,
            status=self._map_status(data.get("status", "PE")),
            raw=data,
        )

    def refund(self, reference: str, amount: Decimal | None = None) -> PaymentResult:
        payload = {"amount": str(amount) if amount else None}
        data = self._post(f"/transactions/{reference}/refund", payload)
        return PaymentResult(
            gateway=self.name,
            reference=reference,
            status=PaymentStatus.REFUNDED,
            raw=data,
        )

    @staticmethod
    def _map_status(pagosnet_status: str) -> str:
        mapping = {
            "PE": PaymentStatus.PENDING,
            "CO": PaymentStatus.COMPLETED,
            "CA": PaymentStatus.DECLINED,
        }
        return mapping.get(pagosnet_status.upper(), PaymentStatus.PENDING)

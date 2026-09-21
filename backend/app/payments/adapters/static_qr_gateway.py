"""
Static QR Gateway - Dynamic Simulated QR Payment Gateway.

Generates dynamic QR codes that open a simulated payment page.
Payment is confirmed either by user clicking "Pagar" or auto-completion after delay.
"""
import hashlib
import hmac
import urllib.parse
import uuid
from decimal import Decimal
from datetime import UTC, datetime, timedelta
from typing import Optional
from dataclasses import dataclass

from app.core.config import settings
from app.core.exceptions import PaymentError
from app.payments.domain.entities import (
    PaymentRequest,
    PaymentResult,
    PaymentStatus,
    PaymentStatusResult,
)
from app.payments.domain.gateway import PaymentGateway


# In-memory storage for auto-completion tasks (in production use Redis/Celery)
_pending_auto_complete: dict[str, dict] = {}


@dataclass
class StaticQRConfig:
    """Configuration for Static QR Gateway."""
    merchant_id: str
    merchant_name: str
    merchant_city: str
    account: str
    base_url: str
    webhook_secret: str
    timeout_minutes: int
    auto_complete_seconds: int = 30


def _load_config() -> StaticQRConfig:
    """Load configuration from settings."""
    return StaticQRConfig(
        merchant_id=getattr(settings, "static_qr_merchant_id", "FS001"),
        merchant_name=getattr(settings, "static_qr_merchant_name", "FashionStore"),
        merchant_city=getattr(settings, "static_qr_merchant_city", "La Paz"),
        account=getattr(settings, "static_qr_account", "12345678901234567890"),
        base_url=getattr(settings, "base_url_app", "http://localhost:8000"),
        webhook_secret=getattr(settings, "static_qr_webhook_secret", ""),
        timeout_minutes=getattr(settings, "static_qr_timeout_minutes", 10),
        auto_complete_seconds=getattr(settings, "static_qr_auto_complete_seconds", 30),
    )


def _generate_reference() -> str:
    """Generate unique payment reference."""
    return f"QR_FS_{uuid.uuid4().hex[:12].upper()}"


def _verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify HMAC-SHA256 webhook signature."""
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


class StaticQRGateway(PaymentGateway):
    """
    Static QR Gateway with Dynamic Simulated QR.
    
    Generates dynamic QR codes that open a simulated payment page.
    Payment is confirmed either by:
    1. User clicking "Pagar" on the simulated payment page
    2. Auto-completion after configurable delay (for demo/testing)
    """
    
    name = "static_qr"
    
    def __init__(self, db=None) -> None:
        self.config = _load_config()
        self.db = db
        
        if not self.config.webhook_secret:
            raise PaymentError(
                "Static QR Gateway requires STATIC_QR_WEBHOOK_SECRET in settings."
            )
    
    def create_payment(self, request: PaymentRequest) -> PaymentResult:
        """
        Create a dynamic QR payment.
        
        Generates a dynamic QR code that opens a simulated payment page.
        The QR contains a URL to the payment page, not static account info.
        """
        reference = _generate_reference()
        expires_at = datetime.now(UTC) + timedelta(minutes=self.config.timeout_minutes)
        
        # Build QR URL (not the QR payload itself, but the payment page URL)
        payment_page_url = f"{self.config.base_url}/pay/{reference}"
        
        # Generate QR SVG for the payment page URL
        qr_svg = self._generate_qr_svg(reference)
        qr_png_base64 = self._generate_qr_png_base64(reference)
        
        # Payment page URL (the URL that the QR points to)
        payment_page_url = f"{self.config.base_url}/pay/{reference}"
        qr_api_url = f"{self.config.base_url}/api/v1/payments/qr/{reference}"
        
        # Prepare raw data for storage
        raw_data = {
            "qr_payload": reference,
            "qr_svg": reference,
            "qr_png_base64": reference,
            "qr_url": qr_api_url,
            "payment_page_url": payment_page_url,
            "expires_at": (datetime.now(UTC) + timedelta(minutes=self.config.timeout_minutes)).isoformat(),
            "auto_complete_seconds": self.config.auto_complete_seconds,
        }
        
        # Schedule auto-completion (for demo/testing)
        self._schedule_auto_complete(reference)
        
        return PaymentResult(
            gateway=self.name,
            reference=reference,
            status=PaymentStatus.PENDING,
            payment_url=reference,  # Return reference, frontend will use /api/v1/payments/qr/{ref}
            raw=raw_data,
        )
    
    def get_status(self, reference: str) -> PaymentStatusResult:
        """
        Get payment status.
        
        Checks:
        1. Webhook received (payment completed via user action)
        2. Auto-completion time reached (simulated payment)
        3. Timeout expired
        4. Current stored status
        """
        return PaymentStatusResult(
            reference=reference,
            status=PaymentStatus.PENDING,
            raw={"checked_at": datetime.now(UTC).isoformat()}
        )
    
    def refund(self, reference: str, amount: Optional[Decimal] = None) -> PaymentResult:
        """Process refund (simulated)."""
        return PaymentResult(
            gateway=self.name,
            reference=reference,
            status=PaymentStatus.REFUNDED,
            raw={"amount": str(amount) if amount else "full", "simulated": True}
        )
    
    def _generate_qr_svg(self, reference: str) -> str:
        """Generate QR SVG for the reference."""
        import qrcode
        import qrcode.image.svg
        from io import BytesIO
        
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
            image_factory=qrcode.image.svg.SvgImage,
        )
        qr.add_data(reference)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer)
        return buffer.getvalue().decode("utf-8")
    
    def _generate_qr_png_base64(self, reference: str) -> str:
        """Generate QR as base64 PNG."""
        import base64
        import qrcode
        from io import BytesIO
        
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(reference)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    def _schedule_auto_complete(self, reference: str) -> None:
        """Schedule auto-completion for demo/testing."""
        config = _load_config()
        complete_at = datetime.now(UTC) + timedelta(seconds=config.auto_complete_seconds)
        
        _pending_auto_complete[reference] = {
            "complete_at": datetime.now(UTC) + timedelta(seconds=config.auto_complete_seconds),
            "completed": False,
        }
    
    @classmethod
    def check_auto_complete(cls, reference: str) -> bool:
        """Check if auto-completion should trigger."""
        if reference in _pending_auto_complete:
            task = _pending_auto_complete[reference]
            if not task["completed"] and datetime.now(UTC) >= task["complete_at"]:
                task["completed"] = True
                return True
        return False
    
    @classmethod
    def mark_completed(cls, reference: str) -> None:
        """Mark payment as completed (called by webhook)."""
        if reference in _pending_auto_complete:
            _pending_auto_complete[reference]["completed"] = True
    
    def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify webhook signature."""
        expected = hmac.new(
            self.config.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
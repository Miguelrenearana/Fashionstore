"""
Tests for CU-25: Procesar pago electrónico (Static QR Gateway)

Tests cover:
- Payment initiation with static_qr gateway
- Payment confirmation via webhook
- Auto-completion fallback
- Refund processing
- Status polling
"""
import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.sales import Payment, Receipt, Sale
from app.payments.adapters.static_qr_gateway import _pending_auto_complete


class TestCU25PaymentStaticQR:
    """Tests for CU-25: Procesar pago electrónico con Static QR Gateway"""

    @pytest.fixture(autouse=True)
    def setup_webhook_secret(self, monkeypatch):
        """Set required webhook secret for tests."""
        # Clear lru_cache on settings to allow monkeypatching
        from app.core.config import get_settings
        from app.payments.factory import get_payment_service
        get_settings.cache_clear()
        get_payment_service.cache_clear()
        monkeypatch.setattr(settings, "static_qr_webhook_secret", "test_secret_123")
        monkeypatch.setattr(settings, "payment_gateway", "static_qr")
        monkeypatch.setattr(settings, "static_qr_auto_complete_seconds", 2)  # Fast for tests
        monkeypatch.setattr(settings, "static_qr_timeout_minutes", 10)
        monkeypatch.setattr(settings, "base_url_app", "http://localhost:8000")
        # Clear auto-complete tracker
        _pending_auto_complete.clear()

    def _sign_payload(self, payload: dict) -> str:
        """Generate HMAC signature for webhook payload."""
        # Use the exact same JSON serialization as the test client
        payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        return hmac.new(
            b"test_secret_123",
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _make_webhook_request(self, client, payload: dict, signature: str = None):
        """Helper to make webhook request with proper signature."""
        if signature is None:
            signature = self._sign_payload(payload)
        payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        return client.post(
            "/api/v1/payments/webhook/static_qr",
            content=payload_str,
            headers={"Content-Type": "application/json", "X-Signature": signature},
        )

    def _create_sale(self, total_amount=Decimal("150.00")):
        """Helper to create a test sale via direct DB."""
        db = SessionLocal()
        try:
            sale = Sale(
                invoice_number=f"TEST-{int(datetime.now(UTC).timestamp())}",
                branch_id=1,
                client_id=1,
                total_amount=total_amount,
                payment_method="static_qr",
                status="PENDING",
            )
            db.add(sale)
            db.commit()
            db.refresh(sale)
            sale_id = sale.id
        finally:
            db.close()
        return sale_id

    def test_initiate_payment_with_static_qr(self, client, client_headers):
        """Test initiating a payment with static_qr gateway."""
        # Create a sale first
        sale_id = self._create_sale(Decimal("150.00"))

        # Initiate payment
        r = client.post(
            f"/api/v1/payments/initiate?sale_id={sale_id}&method=static_qr",
            headers=client_headers,
        )
        assert r.status_code == 200, r.text
        data = r.json()

        # Verify response structure (PaymentRead schema)
        assert "gateway_reference" in data
        assert data["gateway_reference"].startswith("QR_FS_")
        assert data["status"] == "PENDING"
        assert data["sale_id"] == sale_id
        assert data["method"] == "static_qr"
        assert data["amount"] == 150.00
        assert data["currency"] == "BOB"

        # Verify payment record created
        db = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.gateway_reference == data["gateway_reference"]).first()
            assert payment is not None
            assert payment.sale_id == sale_id
            assert payment.status == "PENDING"
            assert payment.method == "static_qr"
        finally:
            db.close()

    def test_payment_webhook_completes_payment(self, client, client_headers):
        """Test webhook completes payment and generates receipt."""
        sale_id = self._create_sale(Decimal("150.00"))

        # Initiate payment
        db = SessionLocal()
        try:
            r = client.post(
                f"/api/v1/payments/initiate?sale_id={sale_id}&method=static_qr",
                headers=client_headers,
            )
        finally:
            db.close()
        assert r.status_code == 200
        reference = r.json()["gateway_reference"]

        # Send webhook to complete payment
        payload = {"reference": reference, "status": "COMPLETED", "amount": 150.00}

        r = self._make_webhook_request(client, payload)
        assert r.status_code == 200, r.text
        assert r.json()["success"] is True

        # Verify payment completed
        db = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
            assert payment.status == "COMPLETED"
            assert payment.qr_verification_method == "webhook"
            assert payment.qr_webhook_received_at is not None

            # Verify sale marked as paid
            sale = db.query(Sale).filter(Sale.id == payment.sale_id).first()
            assert sale.status == "PAID"
            assert sale.paid_at is not None

            # Verify receipt generated
            from app.models.sales import Receipt
            receipt = db.query(Receipt).filter(Receipt.sale_id == sale.id).first()
            assert receipt is not None
            assert receipt.type == "invoice"
        finally:
            db.close()

    def test_auto_complete_payment(self, client, client_headers):
        """Test auto-completion after timeout."""
        # Create sale and payment
        sale_id = self._create_sale(Decimal("150.00"))

        # Initiate payment
        db = SessionLocal()
        try:
            r = client.post(
                f"/api/v1/payments/initiate?sale_id={sale_id}&method=static_qr",
                headers=client_headers,
            )
        finally:
            db.close()
        assert r.status_code == 200
        reference = r.json()["gateway_reference"]

        # Wait for auto-completion (2 seconds in test config)
        import time
        time.sleep(2.5)

        # Poll status - should auto-complete
        r = client.get(f"/api/v1/payments/qr/status/{reference}", headers=client_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "COMPLETED"

        # Verify payment completed in DB
        db = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
            assert payment.status == "COMPLETED"
            assert payment.qr_verification_method == "auto_complete"
        finally:
            db.close()

    def test_payment_timeout(self, client, client_headers):
        """Test payment timeout after expiry."""
        sale_id = self._create_sale(Decimal("150.00"))

        db = SessionLocal()
        try:
            r = client.post(
                f"/api/v1/payments/initiate?sale_id={sale_id}&method=static_qr",
                headers=client_headers,
            )
        finally:
            db.close()
        assert r.status_code == 200
        reference = r.json()["gateway_reference"]

        # Manually expire the payment
        db = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
            payment.qr_expires_at = datetime.now(UTC) - timedelta(minutes=1)
            # Disable auto-complete for this test by setting it far in the future
            from app.payments.adapters.static_qr_gateway import _pending_auto_complete
            _pending_auto_complete[reference] = {
                "complete_at": datetime.now(UTC) + timedelta(hours=1),
                "completed": False,
            }
            db.commit()
        finally:
            db.close()

        # Check status - should be TIMEOUT
        r = client.get(f"/api/v1/payments/qr/status/{reference}")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "TIMEOUT"

    def test_refund_payment(self, client, admin_headers):
        """Test refund processing."""
        # Create a completed sale
        sale_id = self._create_sale(Decimal("150.00"))

        db = SessionLocal()
        try:
            sale = db.query(Sale).filter(Sale.id == sale_id).first()
            sale.status = "PAID"
            sale.paid_at = datetime.now(UTC)
            db.commit()
        finally:
            db.close()

        # Create payment
        reference = f"QR_FS_TESTREFUND{uuid.uuid4().hex[:8]}"
        db = SessionLocal()
        try:
            payment = Payment(
                gateway_reference=reference,
                sale_id=sale_id,
                amount=Decimal("150.00"),
                currency="BOB",
                method="static_qr",
                status="COMPLETED",
            )
            db.add(payment)
            db.commit()
        finally:
            db.close()

        # Refund - gateway_reference is a query parameter, not JSON body
        r = client.post(
            f"/api/v1/payments/refund?gateway_reference={reference}",
            headers=admin_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "REFUNDED"

        # Verify refund
        db = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
            assert payment.status == "REFUNDED"

            # Sale should be REFUNDED
            sale = db.query(Sale).filter(Sale.id == payment.sale_id).first()
            assert sale.status == "REFUNDED"

            # Credit note generated
            credit_note = db.query(Receipt).filter(
                Receipt.sale_id == sale.id, Receipt.type == "credit_note"
            ).first()
            assert credit_note is not None
            assert credit_note.type == "credit_note"
        finally:
            db.close()

    def test_payment_status_polling(self, client, client_headers, monkeypatch):
        """Test status polling endpoint."""
        # Disable auto-complete for this test by setting a very large timeout
        monkeypatch.setattr(settings, "static_qr_auto_complete_seconds", 3600)  # 1 hour

        sale_id = self._create_sale(Decimal("150.00"))

        db = SessionLocal()
        try:
            r = client.post(
                f"/api/v1/payments/initiate?sale_id={sale_id}&method=static_qr",
                headers=client_headers,
            )
        finally:
            db.close()
        assert r.status_code == 200
        reference = r.json()["gateway_reference"]

        # Check status endpoint
        r = client.get(f"/api/v1/payments/qr/status/{reference}", headers=client_headers)
        assert r.status_code == 200
        data = r.json()
        assert data["reference"] == reference
        assert data["status"] == "PENDING"
        assert data["amount"] == 150.00
        assert data["currency"] == "BOB"

    def test_webhook_invalid_signature_rejected(self, client, client_headers):
        """Test webhook with invalid signature is rejected."""
        sale_id = self._create_sale(Decimal("150.00"))

        db = SessionLocal()
        try:
            r = client.post(
                f"/api/v1/payments/initiate?sale_id={sale_id}&method=static_qr",
                headers=client_headers,
            )
        finally:
            db.close()
        assert r.status_code == 200
        reference = r.json()["gateway_reference"]

        # Send webhook with invalid signature
        r = client.post(
            "/api/v1/payments/webhook/static_qr",
            json={"reference": reference, "status": "COMPLETED", "amount": 150.00},
            headers={"Content-Type": "application/json", "X-Signature": "invalid_signature"},
        )
        assert r.status_code == 401
        assert "Invalid signature" in r.text

    def test_webhook_idempotent(self, client, client_headers):
        """Test webhook is idempotent (duplicate calls don't error)."""
        sale_id = self._create_sale(Decimal("150.00"))

        db = SessionLocal()
        try:
            r = client.post(
                f"/api/v1/payments/initiate?sale_id={sale_id}&method=static_qr",
                headers=client_headers,
            )
        finally:
            db.close()
        reference = r.json()["gateway_reference"]

        # Send webhook twice
        payload = {"reference": reference, "status": "COMPLETED", "amount": 150.00}
        signature = self._sign_payload(payload)

        for _ in range(2):
            r = self._make_webhook_request(client, payload)
            assert r.status_code == 200
            assert r.json()["success"] is True

        # Verify only one completion
        db = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
            assert payment.status == "COMPLETED"
            assert payment.qr_verification_method == "webhook"
        finally:
            db.close()

    def test_qr_svg_endpoint(self, client, client_headers):
        """Test QR SVG endpoint returns valid SVG."""
        sale_id = self._create_sale(Decimal("150.00"))

        db = SessionLocal()
        try:
            r = client.post(
                f"/api/v1/payments/initiate?sale_id={sale_id}&method=static_qr",
                headers=client_headers,
            )
        finally:
            db.close()
        reference = r.json()["gateway_reference"]

        # Get SVG
        r = client.get(f"/api/v1/payments/qr/{reference}.svg")
        assert r.status_code == 200
        assert r.headers["content-type"] == "image/svg+xml"
        assert "<svg" in r.text
        # The SVG uses width/height attributes instead of viewBox
        assert 'width="' in r.text
        assert 'height="' in r.text

    def test_payment_page_html(self, client):
        """Test payment page renders HTML with QR and auto-complete."""
        sale_id = self._create_sale(Decimal("150.00"))

        db = SessionLocal()
        try:
            reference = f"QR_FS_TESTPAGE{uuid.uuid4().hex[:8]}"
            payment = Payment(
                gateway_reference=reference,
                sale_id=sale_id,
                amount=Decimal("150.00"),
                currency="BOB",
                method="static_qr",
                status="PENDING",
            )
            db.add(payment)
            db.commit()
        finally:
            db.close()

        r = client.get(f"/api/v1/payments/pay/{reference}")
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
        assert "Pagar Ahora" in r.text
        assert "Pago automático en" in r.text

    def test_gateway_config_endpoint(self, client):
        """Test gateway config endpoint returns correct gateway name."""
        r = client.get("/api/v1/payments/config")
        assert r.status_code == 200
        data = r.json()
        assert data["gateway"] == "static_qr"

    def test_payment_init_request_schema(self):
        """Test PaymentInitRequest schema validation."""
        from app.schemas.payment import PaymentInitRequest

        # Valid request
        req = PaymentInitRequest(sale_id=1, method="static_qr")
        assert req.sale_id == 1
        assert req.method == "static_qr"

        # Invalid method
        with pytest.raises(Exception):
            PaymentInitRequest(sale_id=1, method="invalid_method")

    def test_payment_init_response_schema(self):
        """Test PaymentInitResponse schema."""
        from datetime import UTC, datetime

        from app.schemas.payment import PaymentInitResponse

        resp = PaymentInitResponse(
            reference="QR_FS_TEST123",
            status="PENDING",
            payment_url="http://localhost/pay/QR_FS_TEST123",
            qr_svg_url="/api/v1/payments/qr/QR_FS_TEST123.svg",
            payment_page_url="/pay/QR_FS_TEST123",
            expires_at=datetime.now(UTC),
            raw={},
        )
        assert resp.reference == "QR_FS_TEST123"
        assert resp.status == "PENDING"

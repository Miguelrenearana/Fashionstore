"""
Verification Service for Static QR Gateway.

Handles automatic payment verification via:
1. Webhook notifications (from simulated payment page)
2. Background polling for auto-completion
3. Status checking and state transitions
"""
import hashlib
import hmac
import json
import logging
from datetime import UTC, datetime

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.sales import Payment
from app.payments.adapters.static_qr_gateway import StaticQRGateway, _pending_auto_complete

logger = logging.getLogger(__name__)


class VerificationService:
    """
    Service for automatic payment verification.
    
    Handles:
    - Webhook verification and processing
    - Auto-completion checking
    - Status transitions and side effects
    """

    def __init__(self):
        self.webhook_secret = getattr(settings, "static_qr_webhook_secret", "")

    def process_webhook(self, payload: dict, signature: str) -> dict:
        """
        Process incoming webhook notification.
        
        Validates signature, updates payment status, triggers side effects.
        """
        # Verify signature
        payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        if not self._verify_signature(payload_str, signature):
            return {"success": False, "error": "Invalid signature"}

        reference = payload.get("reference")
        status = payload.get("status")
        amount = payload.get("amount")

        if not reference or not status:
            return {"success": False, "error": "Missing required fields"}

        db = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
            if not payment:
                return {"success": False, "error": "Payment not found"}

            if payment.status == "COMPLETED":
                return {"success": True, "message": "Already completed"}

            # Update payment status
            payment.status = "COMPLETED"
            payment.verified_at = datetime.now(UTC)
            payment.webhook_received_at = datetime.now(UTC)

            # Update sale if linked
            if payment.sale:
                if status == "COMPLETED":
                    payment.sale.status = "PAID"
                    payment.sale.paid_at = datetime.now(UTC)
                    # Generate receipt
                    from app.services.receipt_service import receipt_service
                    receipt_service.generate(db, payment.sale)

            db.commit()
            logger.info(f"Payment {reference} marked as COMPLETED via webhook")
            return {"success": True, "message": "Payment completed"}

        except Exception as e:
            db.rollback()
            logger.error(f"Error processing webhook for {reference}: {e}")
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    def check_auto_complete(self, reference: str) -> bool:
        """Check if auto-completion should trigger for a payment."""
        return StaticQRGateway.check_auto_complete(reference)

    def process_auto_complete(self, reference: str) -> bool:
        """
        Process auto-completion for a payment.
        
        Called by background worker when auto-complete time is reached.
        """
        db = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
            if not payment or payment.status != "PENDING":
                return False

            # Check if auto-complete time has passed
            from app.payments.adapters.static_qr_gateway import StaticQRGateway
            if StaticQRGateway.check_auto_complete(payment.gateway_reference):
                payment.status = "COMPLETED"
                payment.verified_at = datetime.now(UTC)

                if payment.sale:
                    payment.sale.status = "PAID"
                    payment.sale.paid_at = datetime.now(UTC)
                    from app.services.receipt_service import receipt_service
                    receipt_service.generate(db, payment.sale)

                db.commit()
                logger.info(f"Payment {payment.gateway_reference} auto-completed")
                return True

            return False

        except Exception as e:
            db.rollback()
            logger.error(f"Error auto-completing payment {reference}: {e}")
            return False
        finally:
            db.close()

    def check_timeouts(self) -> int:
        """
        Check for expired payments and mark as TIMEOUT.
        
        Returns number of payments timed out.
        """
        db = SessionLocal()
        try:
            expired_payments = db.query(Payment).filter(
                Payment.status == "PENDING",
                Payment.gateway_reference.like("QR_FS_%"),
                Payment.qr_expires_at < datetime.now(UTC)
            ).all()

            count = 0
            for payment in expired_payments:
                payment.status = "TIMEOUT"
                count += 1

            if count > 0:
                db.commit()
                logger.info(f"Marked {count} payments as TIMEOUT")

            return count

        except Exception as e:
            db.rollback()
            logger.error(f"Error checking timeouts: {e}")
            return 0
        finally:
            db.close()

    def _verify_signature(self, payload: str, signature: str) -> bool:
        """Verify HMAC-SHA256 signature."""
        if not self.webhook_secret:
            return False
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


# Background task function for APScheduler
def run_verification_tasks():
    """Background task to run verification checks."""
    service = VerificationService()

    # Check auto-completions
    for reference in list(_pending_auto_complete.keys()):
        if reference not in _pending_auto_complete:
            continue
        task = _pending_auto_complete[reference]
        if not task.get("completed", False):
            # Check if auto-complete time has passed
            complete_at = task.get("complete_at")
            if complete_at and datetime.now(UTC) >= complete_at:
                # Process auto-complete
                db = SessionLocal()
                try:
                    payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
                    if payment and payment.status == "PENDING":
                        payment.status = "COMPLETED"
                        payment.verified_at = datetime.now(UTC)
                        if payment.sale:
                            payment.sale.status = "PAID"
                            payment.sale.paid_at = datetime.now(UTC)
                            from app.services.receipt_service import receipt_service
                            receipt_service.generate(db, payment.sale)
                        db.commit()
                        # Mark as completed in tracking
                        if reference in _pending_auto_complete:
                            _pending_auto_complete[reference]["completed"] = True
                except Exception as e:
                    db.rollback()
                    logging.getLogger(__name__).error(f"Error auto-completing {reference}: {e}")
                finally:
                    db.close()

        # Check timeouts
        service.check_timeouts()


# Standalone function for APScheduler
def run_verification_job():
    """Job function for APScheduler."""
    run_verification_tasks()

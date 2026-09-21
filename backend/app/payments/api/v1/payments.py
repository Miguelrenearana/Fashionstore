import hashlib
import hmac
import json
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.models.sales import Payment, Sale, SalePaymentStatus, SaleStatus
from app.payments.adapters.static_qr_gateway import StaticQRGateway
from app.payments.domain.service import PaymentService
from app.payments.factory import get_payment_service
from app.schemas.payment import PaymentConfirm, PaymentRead
from app.services.receipt_service import receipt_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/config")
def gateway_config():
    service = get_payment_service()
    return {"gateway": service.gateway.name}


@router.post("/initiate", response_model=PaymentRead)
def initiate_payment(
    db: DbSession, sale_id: int, method: str = "card", current: CurrentUser = None
):
    sale = db.get(Sale, sale_id)
    if not sale:
        raise NotFoundError("Sale not found.")
    service: PaymentService = get_payment_service()
    result = service.pay(
        order_reference=f"SALE-{sale.invoice_number}",
        amount=sale.total_amount,
        customer_email=current.email if current else None,
        description=f"FashionStore order {sale.invoice_number}",
    )
    payment = Payment(
        gateway_reference=result.reference,
        sale_id=sale.id,
        amount=sale.total_amount,
        method=method,
        status=result.status,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.post("/confirm")
def confirm_payment(
    db: DbSession,
    payload: PaymentConfirm,
    service: Annotated[PaymentService, Depends(get_payment_service)],
):
    ref = payload.gateway_reference or payload.token
    if not ref:
        raise NotFoundError("Missing payment reference.")
    status_result = service.status(ref)
    payment = db.query(Payment).filter(Payment.gateway_reference == ref).first()
    if payment:
        payment.status = status_result.status
        if payment.sale:
            if status_result.status == SalePaymentStatus.COMPLETED:
                payment.sale.status = SaleStatus.PAID
                payment.sale.paid_at = datetime.now(UTC)
                receipt_service.generate(db, payment.sale)
            elif status_result.status == SalePaymentStatus.DECLINED:
                payment.sale.status = SaleStatus.CANCELLED
        db.commit()
    return {"reference": ref, "status": status_result.status}


@router.post("/refund")
def refund_payment(
    db: DbSession,
    gateway_reference: str,
    service: Annotated[PaymentService, Depends(get_payment_service)],
):
    result = service.refund(gateway_reference)
    payment = db.query(Payment).filter(Payment.gateway_reference == gateway_reference).first()
    if payment:
        payment.status = result.status
        if payment.sale:
            payment.sale.status = SaleStatus.REFUNDED
            if result.status == SalePaymentStatus.REFUNDED:
                receipt_service.generate(db, payment.sale, receipt_type="credit_note")
        db.commit()
    return {"reference": gateway_reference, "status": result.status}


# ============================================================
# Static QR Gateway Endpoints (Dynamic Simulated QR)
# ============================================================

@router.get("/qr/{reference}.svg")
def get_qr_svg(reference: str, db: DbSession):
    """Get QR code as SVG for a payment reference."""
    payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
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
    qr.add_data(payment.gateway_reference)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer)
    svg_content = buffer.getvalue().decode("utf-8")
    
    return Response(content=svg_content, media_type="image/svg+xml")


@router.get("/qr/{reference}")
def get_qr_info(reference: str, db: DbSession):
    """Get QR payment info (amount, merchant, expiry, etc.)"""
    payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    from app.core.config import settings
    config = {
        "merchant_name": getattr(settings, "static_qr_merchant_name", "FashionStore"),
        "merchant_city": getattr(settings, "static_qr_merchant_city", "La Paz"),
    }
    
    return {
        "reference": reference,
        "amount": float(payment.amount),
        "currency": payment.currency,
        "merchant_name": config["merchant_name"],
        "merchant_city": config["merchant_city"],
        "status": payment.status,
        "qr_svg_url": f"/api/v1/payments/qr/{reference}.svg",
        "payment_page_url": f"/pay/{payment.gateway_reference}",
        "expires_at": payment.qr_expires_at,
        "qr_svg_url_direct": f"/api/v1/payments/qr/{reference}.svg",
    }


@router.get("/pay/{reference}", response_class=HTMLResponse)
def payment_page(reference: str, db: DbSession):
    """Simulated payment page - shows QR and payment button."""
    payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    from app.core.config import settings
    merchant_name = getattr(settings, "static_qr_merchant_name", "FashionStore")
    amount = float(payment.amount)
    currency = payment.currency
    
    auto_complete = getattr(settings, "static_qr_auto_complete_seconds", 30)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pago - {merchant_name}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                     max-width: 400px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
            .card {{ background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h2 {{ color: #333; margin-bottom: 8px; }}
            .amount {{ font-size: 2.5rem; font-weight: 700; color: #2c3e50; margin: 16px 0; }}
            .merchant {{ color: #666; margin-bottom: 24px; }}
            .qr-container {{ text-align: center; margin: 24px 0; }}
            .qr-image {{ max-width: 280px; border-radius: 8px; }}
            .btn {{ width: 100%; padding: 16px; font-size: 1.1rem; font-weight: 600; 
                     background: #27ae60; color: white; border: none; border-radius: 8px; cursor: pointer; }}
            .btn:hover {{ background: #219a52; }}
            .timer {{ text-align: center; margin-top: 16px; color: #e74c3c; font-weight: 600; }}
            .footer {{ text-align: center; margin-top: 24px; color: #999; font-size: 0.85rem; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>{merchant_name}</h2>
            <div class="amount">{float(payment.amount):.2f} {payment.currency}</div>
            <p class="merchant">Referencia: {payment.gateway_reference}</p>
            
            <div class="qr-container">
                <img src="/api/v1/payments/qr/{payment.gateway_reference}.svg" alt="QR Code" class="qr-image">
            </div>
            
            <button class="btn" id="payBtn" onclick="payNow()">
                Pagar Ahora
            </button>
            
            <div class="timer" id="timer">
                Pago automático en <span id="countdown">{getattr(settings, "static_qr_auto_complete_seconds", 30)}</span>s
            </div>
            
            <div class="footer">
                <p>Escanea el QR con tu app bancaria o haz clic en "Pagar Ahora"</p>
                <p>Referencia: {payment.gateway_reference}</p>
            </div>
        </div>
        
        <script>
            let countdown = {getattr(settings, "static_qr_auto_complete_seconds", 30)};
            const countdownEl = document.getElementById('countdown');
            const payBtn = document.getElementById('payBtn');
            
            const timer = setInterval(() => {{
                countdown--;
                document.getElementById('countdown').textContent = countdown;
                if (countdown <= 0) {{
                    clearInterval(timer);
                    autoPay();
                }}
            }}, 1000);
            
            function payNow() {{
                fetch('/api/v1/payments/webhook/static_qr', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        reference: '{payment.gateway_reference}',
                        status: 'COMPLETED',
                        amount: {float(payment.amount)}
                    }})
                }}).then(() => {{
                    window.location.href = '/success?ref={payment.gateway_reference}';
                }});
            }}
            
            function autoPay() {{
                fetch('/api/v1/payments/webhook/static_qr', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        reference: '{payment.gateway_reference}',
                        status: 'COMPLETED',
                        amount: {float(payment.amount)}
                    }})
                }}).then(() => {{
                    window.location.href = '/success?ref={payment.gateway_reference}';
                }});
            }}
            
            // Poll for status
            setInterval(async () => {{
                try {{
                    const res = await fetch('/api/v1/payments/qr/status/{payment.gateway_reference}');
                    const data = await res.json();
                    if (data.status === 'COMPLETED') {{
                        window.location.href = '/success?ref={payment.gateway_reference}';
                    }}
                }} catch (e) {{}}
            }}, 5000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.post("/webhook/static_qr")
async def webhook_static_qr(request: Request, db: DbSession):
    """Webhook endpoint for static QR payment confirmation."""
    from app.core.config import settings
    
    webhook_secret = getattr(settings, "static_qr_webhook_secret", "")
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    # Read raw body for signature verification
    body = await request.body()
    body_str = body.decode("utf-8")
    
    # Verify signature
    signature = request.headers.get("X-Signature", "")
    expected = hmac.new(
        getattr(settings, "static_qr_webhook_secret", "").encode(),
        body_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    reference = payload.get("reference")
    status = payload.get("status")
    amount = payload.get("amount")
    
    if not reference or not status:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status == "COMPLETED":
        return {"success": True, "message": "Already completed"}
    
    if status == "COMPLETED":
        payment.status = "COMPLETED"
        payment.qr_verified_at = datetime.now(UTC)
        payment.qr_webhook_received_at = datetime.now(UTC)
        payment.qr_verification_method = "webhook"
        
        if payment.sale:
            payment.sale.status = "PAID"
            payment.sale.paid_at = datetime.now(UTC)
            from app.services.receipt_service import receipt_service
            receipt_service.generate(db, payment.sale)
        
        db.commit()
        return {"success": True, "message": "Payment completed"}
    
    return {"success": False, "message": "Invalid status"}


@router.get("/qr/status/{reference}")
def qr_status(reference: str, db: DbSession):
    """Get QR payment status for frontend polling."""
    payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check auto-completion
    from app.payments.adapters.static_qr_gateway import StaticQRGateway
    if StaticQRGateway.check_auto_complete(payment.gateway_reference):
        payment.status = "COMPLETED"
        payment.qr_verified_at = datetime.now(UTC)
        payment.qr_verification_method = "auto_complete"
        if payment.sale:
            payment.sale.status = "PAID"
            payment.sale.paid_at = datetime.now(UTC)
            from app.services.receipt_service import receipt_service
            receipt_service.generate(db, payment.sale)
        db.commit()
    
    # Check timeout
    if payment.status == "PENDING" and payment.qr_expires_at and datetime.now(UTC) > payment.qr_expires_at:
        payment.status = "TIMEOUT"
        db.commit()
    
    return {
        "reference": payment.gateway_reference,
        "status": payment.status,
        "amount": float(payment.amount),
        "currency": payment.currency,
        "verified_at": payment.qr_verified_at.isoformat() if payment.qr_verified_at else None,
    }

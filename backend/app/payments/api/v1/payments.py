from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.models.sales import Payment, Sale, SalePaymentStatus, SaleStatus
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

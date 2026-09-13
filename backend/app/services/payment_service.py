from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.sales import Payment, Sale, SalePaymentStatus
from app.payments.domain.service import PaymentService
from app.payments.factory import get_payment_service


class PaymentServiceAdapter:
    """Payment facet for sales/reservations flows (uses domain gateway)."""

    def initiate_for_sale(self, db: Session, sale: Sale, email: str | None = None) -> Payment:
        service: PaymentService = get_payment_service()
        result = service.pay(
            order_reference=f"SALE-{sale.invoice_number}",
            amount=sale.total_amount,
            customer_email=email,
            description=f"FashionStore order {sale.invoice_number}",
        )
        payment = Payment(
            gateway_reference=result.reference,
            sale_id=sale.id,
            amount=result.amount if hasattr(result, "amount") else sale.total_amount,
            method=service.gateway.name,
            status=result.status,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    def confirm(self, db: Session, reference: str) -> Payment:
        service: PaymentService = get_payment_service()
        status_result = service.status(reference)
        payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
        if not payment:
            raise NotFoundError("Payment not found by reference.")
        payment.status = status_result.status
        if payment.sale and status_result.succeeded:
            payment.sale.status = SalePaymentStatus.COMPLETED
        db.commit()
        db.refresh(payment)
        return payment

    def refund(self, db: Session, reference: str) -> Payment:
        service: PaymentService = get_payment_service()
        result = service.refund(reference)
        payment = db.query(Payment).filter(Payment.gateway_reference == reference).first()
        if not payment:
            raise NotFoundError("Payment not found by reference.")
        payment.status = result.status
        db.commit()
        db.refresh(payment)
        return payment


payment_service_adapter = PaymentServiceAdapter()

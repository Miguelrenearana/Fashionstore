from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import NotFoundError, ValidationError
from app.models.sales import Payment
from app.models.user import Client
from app.payments.factory import get_payment_service
from app.schemas.cart import CartCheckout, CartItemIn, CartPurchase, CartRead, PurchaseResponse
from app.schemas.payment import PaymentRead
from app.schemas.reservation import ReservationCreate, ReservationItem, ReservationRead
from app.schemas.sale import SaleGenerate, SaleItem, SaleRead
from app.services.cart_service import cart_service
from app.services.reservation_service import reservation_service
from app.services.sales_service import sales_service

router = APIRouter(prefix="/cart", tags=["cart"])


def _client_id(db, user) -> int:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if not client:
        raise NotFoundError("Client profile not found for user.")
    return client.id


@router.get("", response_model=CartRead)
def get_cart(db: DbSession, current: CurrentUser):
    client_id = _client_id(db, current)
    cart = cart_service.get_or_create(db, client_id)
    return cart


@router.post("/items", response_model=CartRead)
def add_item(db: DbSession, payload: CartItemIn, current: CurrentUser):
    client_id = _client_id(db, current)
    cart = cart_service.get_or_create(db, client_id)
    return cart_service.add_item(db, cart, payload.variant_id, payload.quantity)


@router.patch("/items/{variant_id}", response_model=CartRead)
def update_item(db: DbSession, variant_id: int, payload: CartItemIn, current: CurrentUser):
    """CU-20: update the quantity of a cart line."""
    client_id = _client_id(db, current)
    cart = cart_service.get_or_create(db, client_id)
    return cart_service.update_item(db, cart, payload.variant_id, payload.quantity)


@router.delete("/items/{variant_id}", response_model=CartRead)
def remove_item(db: DbSession, variant_id: int, current: CurrentUser):
    """CU-20: remove a line from the cart."""
    client_id = _client_id(db, current)
    cart = cart_service.get_or_create(db, client_id)
    return cart_service.remove_item(db, cart, variant_id)


@router.post("/checkout", response_model=ReservationRead)
def checkout(db: DbSession, payload: CartCheckout, current: CurrentUser):
    client_id = _client_id(db, current)
    cart = cart_service.get_or_create(
        db, client_id, payload.branch_id or None
    )
    if not cart.details:
        raise ValidationError("Cart is empty, cannot checkout.")
    items = [
        ReservationItem(variant_id=d.variant_id, quantity=d.quantity) for d in cart.details
    ]
    reservation = reservation_service.create(
        db,
        client_id,
        ReservationCreate(
            branch_id=payload.branch_id or cart.branch_id,
            items=items,
            notes="Checkout desde el carrito",
        ),
    )
    cart_service.clear(db, cart)
    return reservation


@router.post("/purchase", response_model=PurchaseResponse)
def purchase(db: DbSession, payload: CartPurchase, current: CurrentUser):
    """CU-21: buy directly from the cart (web/mobile digital purchase)."""
    client_id = _client_id(db, current)
    cart = cart_service.get_or_create(db, client_id, payload.branch_id or None)
    if not cart.details:
        raise ValidationError("Cart is empty, cannot purchase.")
    branch_id = payload.branch_id or cart.branch_id
    if not branch_id:
        raise ValidationError("A branch is required to purchase.")
    items = [
        SaleItem(variant_id=d.variant_id, quantity=d.quantity) for d in cart.details
    ]
    sale = sales_service.create_sale(
        db,
        SaleGenerate(branch_id=branch_id, items=items, payment_method=payload.payment_method),
        client_id=client_id,
    )
    service = get_payment_service()
    result = service.pay(
        order_reference=f"SALE-{sale.invoice_number}",
        amount=sale.total_amount,
        customer_email=current.email,
        description=f"FashionStore order {sale.invoice_number}",
    )
    payment = Payment(
        gateway_reference=result.reference,
        sale_id=sale.id,
        amount=sale.total_amount,
        method=payload.payment_method,
        status=result.status,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    cart_service.clear(db, cart)
    return PurchaseResponse(
        sale=SaleRead.model_validate(sale),
        payment=PaymentRead.model_validate(payment),
    )
